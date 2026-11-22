package dev.kagenti.demo.keycloak;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.jboss.logging.Logger;
import org.keycloak.OAuth2Constants;
import org.keycloak.TokenVerifier;
import org.keycloak.models.KeycloakSession;
import org.keycloak.protocol.oidc.TokenExchangeContext;
import org.keycloak.protocol.oidc.TokenExchangeProvider;
import org.keycloak.protocol.oidc.tokenexchange.StandardTokenExchangeProvider;
import org.keycloak.representations.AccessToken;
import org.keycloak.representations.AccessTokenResponse;

import jakarta.ws.rs.core.Response;

/**
 * Token exchange provider that adds RFC 8693 actor claims AND narrows scopes
 * to the intersection of requested and available scopes.
 */
public class AgenticTokenExchangeProvider implements TokenExchangeProvider {

    private static final Logger LOG = Logger.getLogger(AgenticTokenExchangeProvider.class);
    private static final int MAX_ACT_DEPTH = 10;

    private final KeycloakSession session;

    public AgenticTokenExchangeProvider(KeycloakSession session) {
        this.session = session;
    }

    @Override
    public boolean supports(TokenExchangeContext context) {
        return true;
    }

    @Override
    public Response exchange(TokenExchangeContext context) {
        StandardTokenExchangeProvider delegate = new StandardTokenExchangeProvider();
        Response response = delegate.exchange(context);

        if (response.getStatus() != 200) {
            return response;
        }

        Object entity = response.getEntity();
        if (!(entity instanceof AccessTokenResponse tokenResponse)) {
            return response;
        }

        String accessTokenStr = tokenResponse.getToken();
        if (accessTokenStr == null) {
            return response;
        }

        AccessToken accessToken = session.tokens().decode(accessTokenStr, AccessToken.class);
        if (accessToken == null) {
            LOG.warn("Failed to decode exchanged access token");
            return response;
        }

        boolean modified = false;

        modified |= injectActClaim(context, accessToken);
        modified |= narrowScopes(context, accessToken, tokenResponse);

        if (modified) {
            String signed = session.tokens().encode(accessToken);
            tokenResponse.setToken(signed);
        }

        return response;
    }

    private boolean injectActClaim(TokenExchangeContext context, AccessToken accessToken) {
        String actorTokenStr = context.getFormParams().getFirst(OAuth2Constants.ACTOR_TOKEN);
        if (actorTokenStr == null || actorTokenStr.isBlank()) {
            return false;
        }

        try {
            AccessToken actorToken = TokenVerifier.create(actorTokenStr, AccessToken.class).getToken();

            Map<String, Object> actClaim = new LinkedHashMap<>();
            actClaim.put("sub", actorToken.getSubject());
            if (actorToken.getIssuedFor() != null) {
                actClaim.put("client_id", actorToken.getIssuedFor());
            }

            String subjectTokenStr = context.getParams().getSubjectToken();
            if (subjectTokenStr != null) {
                try {
                    AccessToken subjectToken = TokenVerifier.create(subjectTokenStr, AccessToken.class).getToken();
                    Object existingAct = subjectToken.getOtherClaims().get("act");
                    if (existingAct != null) {
                        int depth = countActDepth(existingAct);
                        if (depth < MAX_ACT_DEPTH) {
                            actClaim.put("act", existingAct);
                        } else {
                            LOG.warnf("Act claim chain depth %d exceeds max %d, not nesting further", depth, MAX_ACT_DEPTH);
                        }
                    }
                } catch (Exception e) {
                    LOG.debug("Could not parse subject token for act chain", e);
                }
            }

            accessToken.setOtherClaims("act", actClaim);
            LOG.debugf("Injected act claim: sub=%s", actorToken.getSubject());
            return true;

        } catch (Exception e) {
            LOG.warn("Failed to parse actor token for act claim", e);
            return false;
        }
    }

    private boolean narrowScopes(TokenExchangeContext context, AccessToken accessToken, AccessTokenResponse tokenResponse) {
        String requestedScope = context.getParams().getScope();
        if (requestedScope == null || requestedScope.isBlank()) {
            return false;
        }

        String tokenScope = accessToken.getScope();
        if (tokenScope == null || tokenScope.isBlank()) {
            return false;
        }

        Set<String> requested = parseScopes(requestedScope);
        Set<String> available = parseScopes(tokenScope);

        Set<String> narrowed = new LinkedHashSet<>(available);
        narrowed.retainAll(requested);

        if (available.contains("openid")) {
            narrowed.add("openid");
        }

        if (narrowed.equals(available)) {
            return false;
        }

        String narrowedStr = String.join(" ", narrowed);
        accessToken.setScope(narrowedStr);
        tokenResponse.getOtherClaims().put("scope", narrowedStr);

        LOG.debugf("Narrowed scopes from [%s] to [%s] (requested: [%s])", tokenScope, narrowedStr, requestedScope);
        return true;
    }

    private static Set<String> parseScopes(String scopeStr) {
        return Arrays.stream(scopeStr.split("\\s+"))
                .filter(s -> !s.isBlank())
                .collect(Collectors.toCollection(LinkedHashSet::new));
    }

    @SuppressWarnings("unchecked")
    private static int countActDepth(Object act) {
        int depth = 0;
        Object current = act;
        while (current instanceof Map) {
            depth++;
            current = ((Map<String, Object>) current).get("act");
        }
        return depth;
    }

    @Override
    public int getVersion() {
        return 0;
    }

    @Override
    public void close() {
    }
}
