pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:$PATH"
        DOCKER_IMAGE_NAME = "udaykiran03/flaskproj"
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                git url: 'https://github.com/Udaykiran2727/flaskproj.git', branch: 'main'
            }
        }
        
        stage('2. Build Docker Image') {
            steps {
                script {
                    def imageName = "${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    echo "Building ${imageName}..."
                    docker.build(imageName, ".")
                    
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

                    echo "Starting test container for ${imageName} in TEST_MODE..."
                    
                    // --- THIS IS NOW CORRECTED ---
                    // 1. Add '-e TEST_MODE=True' to set the environment variable
                    sh "docker run -d --name flask-test -e TEST_MODE=True -p 8000:5000 ${imageName}"
                    
                    echo "Waiting 10s for app to start..."
                    sh 'sleep 10' 
                    
                    // --- THIS IS NOW CORRECTED ---
                    // 1. Test the new '/' health check route
                    echo "Testing http://localhost:8000/ ..."
                    sh 'curl -f http://localhost:8000/'
                    echo "Test successful!"
                }
            }
            post {
                always {
                    echo "--- Grabbing container logs for debugging ---"
                    sh 'docker logs flask-test || true' 
                    
                    echo "--- Stopping and removing test container ---"
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

                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        echo "Logging in to Docker Hub as $DOCKER_USER..."
                        sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                        
                        echo "Pushing ${imageName} to Docker Hub..."
                        docker.image(imageName).push()
                        
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
                    
                    // This deployment will use the REAL MySQL database
                    // because we are NOT setting TEST_MODE=True
                    sh 'docker stop flask-prod || true'
                    sh 'docker rm flask-prod || true'
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