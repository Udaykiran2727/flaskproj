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
                    // This command runs on localhost, so proxy is not an issue here
                    sh "docker run -d --name flask-test -e TEST_MODE=True -p 8000:5000 ${imageName}"
                    
                    echo "Waiting 10s for app to start..."
                    sh 'sleep 10' 
                    
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
                        
                        // --- THIS IS THE FIX ---
                        // We explicitly set proxy variables to empty strings to override them
                        echo "Pushing ${imageName} to Docker Hub (overriding proxy)..."
                        withEnv([
                            'http_proxy=',
                            'https_proxy=',
                            'HTTP_PROXY=',
                            'HTTPS_PROXY='
                        ]) {
                            docker.image(imageName).push()
                        }
                        // --- END OF FIX ---
                        
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
                    
                    // --- APPLYING FIX HERE TOO ---
                    // This 'docker run' pulls the image, so it also needs the proxy override
                    withEnv([
                        'http_proxy=',
                        'https_proxy=',
                        'HTTP_PROXY=',
                        'HTTPS_PROXY='
                    ]) {
                        sh 'docker stop flask-prod || true'
                        sh 'docker rm flask-prod || true'
                        sh "docker run -d --name flask-prod -p 8080:5000 ${imageName}"
                    }
                    // --- END OF FIX ---
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