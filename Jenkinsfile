// Works on both Windows (bat) and Linux/Mac (sh) Jenkins
def run(String cmd) {
    if (isUnix()) { sh cmd } else { bat cmd }
}

pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'YOUR_DOCKERHUB_USERNAME'   // <-- change this
        IMAGE          = "${vyshitha}/expense-splitter"
    }

    triggers {
        pollSCM('* * * * *')   // checks Git every minute
    }

    stages {
        stage('Pull Code') {
            steps { checkout scm }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    run("docker build -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .")
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    script {
                        if (isUnix()) {
                            sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                        } else {
                            bat 'echo %DH_PASS%| docker login -u %DH_USER% --password-stdin'
                        }
                        run("docker push ${IMAGE}:${BUILD_NUMBER}")
                        run("docker push ${IMAGE}:latest")
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    script {
                        run('kubectl apply -f k8s/')
                        run("kubectl set image deployment/expense-splitter app=${IMAGE}:${BUILD_NUMBER}")
                        run('kubectl rollout status deployment/expense-splitter --timeout=120s')
                    }
                }
            }
        }
    }
}
