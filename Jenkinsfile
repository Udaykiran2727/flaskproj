pipeline {
    agent any

    // This block runs for the whole pipeline
    environment {
        // Ensures 'docker' is found, just in case the global setting isn't picked up
        PATH = "/usr/local/bin:$PATH"
        
        // --- !!! EDIT THIS !!! ---
        // Change 'your-dockerhub-id' to your actual Docker Hub username
        DOCKER_IMAGE_NAME = "your-dockerhub-id/flaskproj"
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
                    // Tag the image with the build number (e.g., udaykiran2727/flaskproj:3)
                    def imageName = "${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    docker.build(imageName, ".")
                    
                    // We must pass the 'imageName' to the next stages
                    // We do this by writing it to a file and "stashing" it.
                    sh "echo ${imageName} > imageName.txt"
                    stash name: 'imageNameFile', includes: 'imageName.txt'
                }
            }
        }

        stage('3. Run & Test') {
            steps {
                script {
                    // "Unstash" the file to get the image name from the previous stage
                    unstash 'imageNameFile'
                    def imageName = sh(script: 'cat imageName.txt', returnStdout: true).trim()

                    echo "Starting test container for ${imageName}..."
                    // Run the new container in the background, named 'flask-test'
                    // We map port 8000 on the Jenkins host to port 5000 in the container
                    // (I'm assuming your Flask app runs on 5000)
                    sh 'docker run -d --name flask-test -p 8000:5000 ${imageName}'
                    
                    // Wait 10 seconds for the app to start up
                    sh 'sleep 10' 
                    
                    echo "Testing http://localhost:8000 ..."
                    // Use 'curl' to test the app. '-f' makes it fail if it gets an error (like 404 or 500)
                    sh 'curl -f http://localhost:8000/'
                    echo "Test successful!"
                }
            }
            post {
                // This 'always' block runs whether the test passed OR failed
                // This ensures we ALWAYS clean up the test container
                always {
                    echo "Stopping and removing test container..."
                    // '|| true' means "don't fail the build if this command fails"
                    // (which it would if the container never started)
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

                    // Use the Jenkins Credential ID you created in Step 1
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        
                        echo "Logging in to Docker Hub as $DOCKER_USER..."
                        // Log in to Docker using the secret variables
                        sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                        
                        echo "Pushing ${imageName} to Docker Hub..."
                        docker.push(imageName)
                        
                        echo "Logging out..."
                        sh 'docker logout'
                    }
                }
            }
        }

        // --- OPTIONAL DEPLOY STAGE ---
        stage('5. Deploy (Simple Local)') {
            steps {
                script {
                    unstash 'imageNameFile'
                    def imageName = sh(script: 'cat imageName.txt', returnStdout: true).trim()
                    
                    echo "Deploying new 'flask-prod' container to http://localhost:8080"
                    
                    // Stop and remove the old 'prod' container, if it exists
                    sh 'docker stop flask-prod || true'
                    sh 'docker rm flask-prod || true'
                    
                    // Run the new container, mapping to port 8080
                    sh 'docker run -d --name flask-prod -p 8080:5000 ${imageName}'
                }
            }
        }
        
    } // end of stages
    
    post {
        // This runs at the end of the entire pipeline
        always {
            // Clean up the workspace
            cleanWs()
            // Clean up the stashed file
            deleteDir() 
        }
    }
}