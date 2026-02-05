pipeline {
    agent any

    options {
        buildDiscarder logRotator(numToKeepStr: '20')
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
    }

    environment {
        // Configuration
        UPSTREAM_GIT_URL        = 'https://voidpoint.io/terminx/eduke32.git'
        COPR_PROJECT            = 'nost23/eduke32'
        PACKAGING_REPO_URL      = 'https://nostovo.arnostdudek.cz:8085/nost23/eduke32-spec.git'
        PACKAGE_NAME            = 'eduke32'

        // Image with copr-cli
        REGISTRY                = 'nostovo.arnostdudek.cz:32769'
        IMAGE_NAME              = 'copr-builder'

        // Credentials
        COPR_CONFIG_ID          = 'copr-auth'      // ID of secret file credential
        DOCKER_CRED_ID          = 'nexus-jenkins'  // ID of username/password credential for image pulls
        GIT_CRED_ID             = 'forgejo-token'  // ID of username/password credential for pushing
    }

    stages {
        stage('Check Versions') {
            steps {
                script {
                    // Get Upstream Hash (Remote)
                    // Note: git ls-remote returns: <hash>\tHEAD
                    def remoteHash = sh(returnStdout: true, script: "git ls-remote ${UPSTREAM_GIT_URL} HEAD | awk '{print \$1}'").trim()
                    echo "Upstream Hash: ${remoteHash}"

                    // Get Local Hash (from Spec file)
                    // Note: We extract the value defined in %global commit
                    def localHash = sh(returnStdout: true, script: "grep '%global commit' ${PACKAGE_NAME}.spec | awk '{print \$3}'").trim()
                    echo "Local Spec Hash: ${localHash}"

                    // Compare
                    if (remoteHash == localHash) {
                        echo "No changes detected. Skipping build."
                        currentBuild.result = 'SUCCESS'
                        env.UPDATE_NEEDED = 'false'
                    } else {
                        echo "New version detected! Preparing update."
                        env.UPDATE_NEEDED = 'true'
                        env.NEW_HASH = remoteHash
                    }
                }
            }
        }

        stage('Lint') {
            when { environment name: 'UPDATE_NEEDED', value: 'true' }
            // Run inside the container where rpmdevtools/copr-cli are installed
            agent {
                docker {
                    alwaysPull true
                    image "${REGISTRY}/${IMAGE_NAME}"
                    registryCredentialsId DOCKER_CRED_ID
                    registryUrl "https://${REGISTRY}"
                    reuseNode true
                }
            }
            steps {
                sh "rpmlint ${PACKAGE_NAME}.spec"
            }
        }

        stage('Update Spec & Push') {
            when { environment name: 'UPDATE_NEEDED', value: 'true' }
            agent {
                docker {
                    alwaysPull true
                    image "${REGISTRY}/${IMAGE_NAME}"
                    registryCredentialsId DOCKER_CRED_ID
                    registryUrl "https://${REGISTRY}"
                    args '--add-host nostovo.arnostdudek.cz:192.168.1.2'
                    reuseNode true
                }
            }
            steps {
                script {
                    // Generate new date string (YYYYMMDD)
                    def newDate = sh(returnStdout: true, script: "date +%Y%m%d").trim()
                    def shortHash = env.NEW_HASH.take(8)

                    // Replace Commit Hash in Spec
                    sh "sed -i 's/^%global commit .*/%global commit ${env.NEW_HASH}/' ${PACKAGE_NAME}.spec"

                    // Replace Date in Spec
                    sh "sed -i 's/^%global date .*/%global date ${newDate}/' ${PACKAGE_NAME}.spec"

                    // Debug: Verify change
                    sh "grep '%global' ${PACKAGE_NAME}.spec"

                    // Bump Release & Add Changelog (rpmdev-bumpspec)
                    // -u: Sets the user for the changelog entry
                    // -c: The comment to add
                    // This command automatically increments the first number in 'Release'
                    // and prepends a correctly formatted changelog entry.
                    sh """
                        rpmdev-bumpspec \
                        --comment "Automated update to upstream commit ${shortHash}" \
                        --userstring "Jenkins <jenkins@nostovo>" \
                        ${PACKAGE_NAME}.spec
                    """

                    // Debug: Use rpmspec to query the fully expanded Release field
                    sh "rpmspec -q --qf 'Release: %{RELEASE}\n' ${PACKAGE_NAME}.spec"
                    // Debug: Show what happened with changelog
                    sh "grep -A 5 '%changelog' ${PACKAGE_NAME}.spec"

                    // Configure Git Identity
                    sh 'git config user.email "jenkins@nostovo"'
                    sh 'git config user.name "Jenkins"'
                    
                    // Commit changes locally
                    sh "git add ${PACKAGE_NAME}.spec"
                    sh "git commit -m 'chore: Auto-update to upstream commit ${NEW_HASH}'"

                    // PUSH via HTTPS (Dynamic URL Injection)
                    // We reuse the existing 'origin' URL but inject credentials
                    withCredentials([usernamePassword(credentialsId: GIT_CRED_ID, usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                        sh '''
                            # Get the current remote URL (e.g., https://domain.com/repo.git)
                            ORIGIN_URL=$(git remote get-url origin)

                            # Strip the protocol (https://) to get just the domain/path
                            URL_WITHOUT_PROTO=${ORIGIN_URL#*://}

                            # Push using the constructed URL with auth
                            # Structure: https://<user>:<token>@<domain/path>
                            git push "https://${GIT_USER}:${GIT_TOKEN}@${URL_WITHOUT_PROTO}" HEAD:main
                        '''
                    }
                }
            }
        }

        stage('Trigger COPR Build') {
            when { environment name: 'UPDATE_NEEDED', value: 'true' }
            agent {
                docker {
                    alwaysPull true
                    image "${REGISTRY}/${IMAGE_NAME}"
                    registryCredentialsId DOCKER_CRED_ID
                    registryUrl "https://${REGISTRY}"
                    reuseNode true
                }
            }
            steps {
                withCredentials([file(credentialsId: COPR_CONFIG_ID, variable: 'COPR_CONFIG_FILE')]) {
                    // Trigger build and WAIT for result (it pulls what we just pushed)
                    // NOTE: use single-quotes around sensitive variables. https://jenkins.io/redirect/groovy-string-interpolation
                    sh 'copr-cli --config ${COPR_CONFIG_FILE} buildscm ${PACKAGE_NAME} --clone-url ${PACKAGING_REPO_URL} --spec ${PACKAGE_NAME}.spec'
                }
            }
        }
    }
}