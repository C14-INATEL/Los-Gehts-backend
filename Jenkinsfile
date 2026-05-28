pipeline {
    agent any

    environment {
        SECRET_KEY   = credentials('secret-key')
        DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/losgehts_test'
        PYTHON       = 'C:\\Users\\Bedro\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
        PRISMA       = 'C:\\Users\\Bedro\\AppData\\Local\\Programs\\Python\\Python314\\Scripts\\prisma.exe'
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
                to: 'phenriquelmarques4@gmail.com,nathaliaaparecida1804@gmail.com,victorgorgal@gmail.com',
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
                to: 'phenriquelmarques4@gmail.com,nathaliaaparecida1804@gmail.com,victorgorgal@gmail.com',
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
