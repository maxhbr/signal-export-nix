{ lib
, python3
, fetchFromGitHub
, nix-update-script
, sqlcipher3-wheels
, ...
}:
python3.pkgs.buildPythonApplication rec {
  pname = "signal-export";
  version = "3.1.0";
  pyproject = true;

  src = ./.;

  # postPatch = ''
  #    substituteInPlace pyproject.toml \
  #       --replace-fail '"sqlcipher3-wheels >= 0.5.2.post1"' '"pysqlcipher3 >= 1.2.0"'
  #    substituteInPlace requirements.lock \
  #       --replace-fail 'sqlcipher3-wheels==0.5.2.post1' 'pysqlcipher3==1.2.0'
  # '';


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
    # pysqlcipher3
    sqlcipher3-wheels
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
