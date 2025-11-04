pipeline {
    agent any

    environment {
        // Ensures 'docker' is found
        PATH = "/usr/local/bin:$PATH"
        
        // --- THIS IS NOW CORRECTED ---
        DOCKER_IMAGE_NAME = "udaykiran2727/flaskproj"
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                // This 'checkout scm' is automatic when using 'Pipeline from SCM',
                // but explicitly adding it here is good practice.
                git url: 'https://github.com/Udaykiran2727/flaskproj.git', branch: 'main'
            }
        }
        
        stage('2. Build Docker Image') {
            steps {
                script {
                    def imageName = "${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    echo "Building ${imageName}..."
                    docker.build(imageName, ".")
                    
                    // Stash the image name for later stages
                    sh "echo ${imageName} > imageName.txt"
                    stash name: 'imageNameFile', includes: 'imageName.txt'
                }
            }
        }

        stage('3. Run & Test') {
            steps {
                script {
                    unstash 'imageNameFile'
                    def imageName = sh(script: 'cat imageName.txt', returnStdout: true).trim()

                    echo "Starting test container for ${imageName}..."
                    
                    // --- THIS IS NOW CORRECTED (using double quotes) ---
                    sh "docker run -d --name flask-test -p 8000:5000 ${imageName}"
                    
                    sh 'sleep 10' 
                    
                    echo "Testing http://localhost:8000 ..."
                    sh 'curl -f http://localhost:8000/'
                    echo "Test successful!"
                }
            }
            post {
                always {
                    echo "Stopping and removing test container..."
                    sh 'docker stop flask-test || true'
                    sh 'docker rm flask-test || true'
                }
            }
        }
        
        stage('4. Push to Docker Hub') {
            steps {
                script {
                    unstash 'imageNameFile'
                    def imageName = sh(script: 'cat imageName.txt', returnStdout: true).trim()

                    // Use the Credential ID 'dockerhub-creds'
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        
                        echo "Logging in to Docker Hub as $DOCKER_USER..."
                        sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                        
                        echo "Pushing ${imageName} to Docker Hub..."
                        docker.push(imageName)
                        
                        echo "Logging out..."
                        sh 'docker logout'
                    }
                }
            }
        }

        stage('5. Deploy (Simple Local)') {
            steps {
                script {
                    unstash 'imageNameFile'
                    def imageName = sh(script: 'cat imageName.txt', returnStdout: true).trim()
                    
                    echo "Deploying new 'flask-prod' container to http://localhost:8080"
                    
                    sh 'docker stop flask-prod || true'
                    sh 'docker rm flask-prod || true'
                    
                    // --- THIS IS NOW CORRECTED (using double quotes) ---
                    sh "docker run -d --name flask-prod -p 8080:5000 ${imageName}"
                }
            }
        }
        
    } // end of stages
    
    post {
        always {
            cleanWs()
            deleteDir() 
        }
    }
}