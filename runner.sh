echo "Checking OS"

check_os() {
    case "$(uname -s)" in
        Darwin*) echo "macOS" ;;
        CYGWIN*|MINGW*) echo "Windows" ;;
        *) echo "Unknown OS" ;;
    esac
}

os_type=$(check_os)

if [[ "$os_type" == "Windows" ]]; then
    echo "opening docker desktop Win"
    docker desktop start
elif [[ "$os_type" == "macOS" ]]; then
    echo "opening docker desktop MacOS"
    open -a Docker  
elif [[ "$os_type" == "Linux" ]]; then
    echo "Docker Desktop is not available on Linux. Please ensure Docker Engine is running."
else
    echo "Unknown OS, Docker Desktop cannot be started."
fi

docker-compose down -v --remove-orphans
docker network prune -f
docker-compose build --no-cache
docker-compose up -d

check_service() {
    local max_attempts=30 attempt=1 delay=5
    echo "Performing service health check..."

    while [ $attempt -le $max_attempts ]; do
        http_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/home)

        if [ "$http_status" -eq 200 ]; then
            echo "Health check passed! Service is ready."
            return 0
        fi

        sleep $delay
        attempt=$((attempt + 1))
    done

    echo "Health check failed after $max_attempts attempts"
    return 1
}

if check_service; then
    case "$(uname -s)" in
        Linux*) xdg-open "http://localhost:5000/home" ;;
        Darwin*) open "http://localhost:5000/home" ;;
        CYGWIN*|MINGW*) start "http://localhost:5000/home" ;;
        *) echo "Open manually: http://localhost:5000/home" ;;
    esac
fi

read -p "Press any key to exit..."
echo "exiting . . . ."
docker-compose down
exit