(
    git clone $OAI /install/oai &&
    cp -rf /install/oai/user_n/* /app/apps/api/v1/oai/ &&
    rm /app/apps/api/v1/oai/README.md
)