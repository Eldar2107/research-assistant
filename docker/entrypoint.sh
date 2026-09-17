#!/bin/sh
set -e

# Verilənlər bazasının hazır olmasını yoxla (check_db.py mövcuddursa)
if [ -f "check_db.py" ]; then
    echo "Verilənlər bazası yoxlanılır..."
    python check_db.py
fi

# Əsas komandanı icra et
exec "$@"