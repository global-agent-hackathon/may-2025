docker buildx build --platform linux/amd64 -t europe-west1-docker.pkg.dev/agno-agents/slackbot-container-repo/slack-bot:latest .
docker push europe-west1-docker.pkg.dev/agno-agents/slackbot-container-repo/slack-bot:latest
