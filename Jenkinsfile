pipeline {
    agent any 

    stages {
        stage('1. Checkout Code') {
            // ...
        }
        stage('2. Build Docker Image') {
            steps {
                script {
                    echo "Building the Docker image..."
                    
                    // --- THIS IS THE FIX ---
                    // We add /usr/local/bin (where docker lives on macOS) to the PATH
                    withEnv(["PATH+Docker=/usr/local/bin"]) {
                        
                        def imageName = "udaykiran2727/flaskproj:${env.BUILD_NUMBER}"
                        
                        // This command will now be able to find 'docker'
                        docker.build(imageName, ".") 
                        
                        echo "Successfully built ${imageName}"
                    }
                    // --- END OF FIX ---
                }
            }
        }
    }
    // ...
}
