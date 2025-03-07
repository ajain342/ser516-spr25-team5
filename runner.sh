set -a
source .env
set +a

URL="http://localhost:$CONTROLLER_PORT/home"

check_os() {
    case "$(uname -s)" in
        Darwin*) echo "macOS" ;;
        CYGWIN*|MINGW*) echo "Windows" ;;
        *) echo "Unknown OS" ;;
    esac
}
exit_terminal(){
    read -p "Press any key to exit..."
    echo "exiting . . . ."
    docker-compose down
    exit
}

echo "Checking OS"
os_type=$(check_os)

check_port(){
    if [[ "$os_type" == "Windows" ]]; then
        if netstat -ano | grep -q ":$CONTROLLER_PORT "; then
            return 1
        fi
    elif [[ "$os_type" == "macOS" ]]; then
        if lsof -i :$CONTROLLER_PORT >/dev/null 2>&1; then
            return 1
        fi
    echo "Unexpected behaviour while checking port availability"
    return 0
    fi
}

echo "Checking port $CONTROLLER_PORT availability..."
if ! check_port; then
    echo "ERROR: Port $CONTROLLER_PORT is already in use. Please free the port and try again."
    exit_terminal
fi

if [[ "$os_type" == "Windows" ]]; then
    echo "opening docker desktop Win"
    docker desktop start
elif [[ "$os_type" == "macOS" ]]; then
    echo "opening docker desktop MacOS"
    open -a Docker  
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
        http_status=$(curl -s -o /dev/null -w "%{http_code}" $URL)

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
    case "$os_type" in
        macOS) open $URL ;;
        Windows) start $URL ;;
        *) echo "Open manually at - $URL";;
    esac
fi

exit_terminal