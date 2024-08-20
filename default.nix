{ lib
, python3
, fetchFromGitHub
, nix-update-script
, ...
}:
python3.pkgs.buildPythonApplication rec {
  pname = "signal-export";
  version = "3.1.0";
  pyproject = true;

  src = ./.;

  nativeBuildInputs = with python3.pkgs; [
    setuptools-scm
    pdm-backend
  ];

  propagatedBuildInputs = with python3.pkgs; [
    setuptools
    typer
    beautifulsoup4
    emoji
    markdown
    pysqlcipher3
    pycryptodome
  ];

  passthru.updateScript = nix-update-script { };

  meta = with lib; {
    mainProgram = "sigexport";
    homepage = "https://github.com/carderne/signal-export";
    description = "Export your Signal chats to markdown files with attachments";
    platforms = platforms.unix;
    license = licenses.mit;
    maintainers = with maintainers; [ phaer picnoir ];
  };
}
