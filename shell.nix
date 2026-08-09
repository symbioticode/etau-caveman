{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python312;
  pythonEnv = python.withPackages (ps: with ps; [
    python-dotenv
    requests
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.gcc
    pkgs.pkg-config
    pkgs.stdenv.cc.cc.lib
    pkgs.zlib
    pkgs.openssl
    pkgs.cacert
    pkgs.python3Packages.python-dotenv
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:${pkgs.openssl.out}/lib:$LD_LIBRARY_PATH"
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:${pkgs.zlib}/lib/pkgconfig:$PKG_CONFIG_PATH"
    export NIX_SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
    export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"

    VENV_DIR=".venv"

    if [ -d "$VENV_DIR" ]; then
      VENV_PY=$("$VENV_DIR/bin/python" --version 2>&1 | cut -d' ' -f2)
      NIX_PY=$(python --version 2>&1 | cut -d' ' -f2)
      if [ "$VENV_PY" != "$NIX_PY" ]; then
        echo "⚠  Version Python diverge — recréation venv..."
        rm -rf "$VENV_DIR"
      fi
    fi

    if [ ! -d "$VENV_DIR" ]; then
      echo "📦 Création du venv Python $(python --version)..."
      python -m venv "$VENV_DIR" --system-site-packages
    fi

    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel --quiet
    pip install --quiet -r requirements.txt

    export PYTHONPATH="$(pwd):$PYTHONPATH"

    PY="$VENV_DIR/bin/python"
    echo ""
    echo "📊 Dépendances :"
    $PY -c "import requests; print('   ✓ requests:', requests.__version__)" 2>/dev/null || echo "   ✗ requests"
    $PY -c "import dotenv; print('   ✓ python-dotenv')" 2>/dev/null || echo "   ✗ python-dotenv"

    echo ""
    echo "✅ Environnement CAVEMAN prêt — Python: $($PY --version)"
  '';

  PYTHON_KEYRING_BACKEND = "keyring.backends.null.Keyring";
}
