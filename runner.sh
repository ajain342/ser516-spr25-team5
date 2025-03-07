docker-compose down -v --remove-orphans
docker network prune -f
docker-compose build --no-cache
docker-compose up -d

# Health check in main terminal
check_service() {
    local max_attempts=30 attempt=1 delay=5
    echo "Performing service health check..."

    while [ $attempt -le $max_attempts ]; do
        # Check if curl is installed and available for use
        if command -v curl &>/dev/null; then
            http_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/home)
        elif command -v wget &>/dev/null; then
            # Fallback to wget if curl is not available
            http_status=$(wget --spider -q --server-response http://localhost:5000/home 2>&1 | grep "HTTP/" | awk '{print $2}')
        else
            echo "Neither curl nor wget is available. Health check cannot be performed."s
        fi

        if [ "$http_status" -eq 200 ]; then
            echo "Health check passed! Service is ready."
        fi

        sleep $delay
        attempt=$((attempt + 1))
    done

    echo "Health check failed after $max_attempts attempts"
}

# Final check before opening browser
if check_service; then
    case "$(uname -s)" in
        Linux*) xdg-open "http://localhost:5000/home" ;;
        Darwin*) open "http://localhost:5000/home" ;;
        CYGWIN*|MINGW*) start "http://localhost:5000/home" ;;  # For Windows (MSYS/Cygwin environments)
        *) echo "Open manually: http://localhost:5000/home" ;;
    esac
fi
