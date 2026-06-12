pipeline {
    agent any

    environment {
        EMAIL_RECIPIENTS = credentials('jenkins-email-recipients')

        // Configuracoes do Docker Hub
        DOCKER_IMAGE = "${DOCKER_HUB_CREDS_USR}/c14-np2"
        DOCKER_TAG = "${BUILD_NUMBER}"

        DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/losgehts_test'
        PYTHON       = './venv/Scripts/python.exe'
        PRISMA       = './venv/Scripts/prisma.exe'
    }

    stages {

        // ── BUILD ──────────────────────────────────────────────────────────
        stage('Build') {
            steps {
                bat '''
                    "%PYTHON%" -m pip install --upgrade pip
                    "%PYTHON%" -m pip install -r requirements.txt
                '''
            }
        }

        // ── TESTES ────────────────────────────────────────────────────────
        stage('Testes') {
            steps {
                bat '''
                    "%PRISMA%" generate --schema=prisma\\schema.prisma
                    "%PRISMA%" db push --schema=prisma\\schema.prisma
                    "%PYTHON%" -m pytest --tb=short -v
                '''
            }
        }

        // ── VERIFICACAO ───────────────────────────────────────────────────
        stage('Verificacao') {
            steps {
                bat '''
                    "%PYTHON%" -m pip install flake8
                    "%PYTHON%" -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                    "%PYTHON%" -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo 'Building Docker images...'
                    sh """
                        docker build -f Dockerfile -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Push to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo 'Pushing image to Docker Hub...'
                    sh """
                        echo "${DOCKER_HUB_CREDS_PSW}" | docker login -u "${DOCKER_HUB_CREDS_USR}" --password-stdin
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                        docker logout
                    """
                }
            }
        }

        // ── DEPLOY ────────────────────────────────────────────────────────
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploy configurado - adicione o webhook aqui quando tiver o servidor'
            }
        }
    }

    // ── NOTIFICACAO ───────────────────────────────────────────────────────
    post {
        success {
            emailext(
                to: "${EMAIL_RECIPIENTS}",
                subject: "[Los Geht's] Pipeline OK - ${env.BRANCH_NAME}",
                body: """
Repositorio : ${env.JOB_NAME}
Branch      : ${env.BRANCH_NAME}
Build       : ${env.BUILD_NUMBER}
Status      : SUCESSO

Veja o log em: ${env.BUILD_URL}
"""
            )
        }
        failure {
            emailext(
                to: "${EMAIL_RECIPIENTS}",
                subject: "[Los Geht's] Pipeline FALHOU - ${env.BRANCH_NAME}",
                body: """
Repositorio : ${env.JOB_NAME}
Branch      : ${env.BRANCH_NAME}
Build       : ${env.BUILD_NUMBER}
Status      : FALHOU

Veja o log em: ${env.BUILD_URL}
"""
            )
        }
    }
}
