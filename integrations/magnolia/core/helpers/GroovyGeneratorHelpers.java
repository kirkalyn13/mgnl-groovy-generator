package com.sample.cms.helpers;

import info.magnolia.cms.security.SecurityUtil;
import info.magnolia.context.MgnlContext;
import info.magnolia.jcr.util.PropertyUtil;

import javax.jcr.Node;
import javax.jcr.RepositoryException;
import javax.jcr.Session;

import static sanofi.campus.constants.GroovyGeneratorConstants.*;

public class GroovyGeneratorHelpers {

    private GroovyGeneratorHelpers() {}

    /**
     * Retrieves and decrypts the groovy generator keystore values.
     *
     * @return the decrypted keystore value
     */
    public static String getKeystoreValue(String path) throws RepositoryException {
        Session session = MgnlContext.getJCRSession(KEYSTORE_WORKSPACE);
        Node tokenNode = session.getNode(path);
        String encryptedToken = PropertyUtil.getString(tokenNode, PASSWORD_PROPERTY);

        return SecurityUtil.decrypt(encryptedToken);
    }

    /**
     * Builds the full Groovy Generator API URL for the given script and endpoint paths.
     *
     * @param endpointPath the endpoint path of the groovy generator function
     * @param scriptPath the JCR path of the target script node
     * @return the full URL string for the Groovy Generator endpoint
     * @throws RepositoryException if the Groovy Generator path cannot be retrieved
     */
    public static String getGroovyGeneratorUrl(String endpointPath, String scriptPath) throws RepositoryException {
        return String.format("%s%s%s", getKeystoreValue(GROOVY_GENERATOR_PATH), endpointPath, scriptPath);
    }
}