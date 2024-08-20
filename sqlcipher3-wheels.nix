{ lib
, python3
, fetchPypi
, sqlcipher
, openssl
, conan
, ...
}:
python3.pkgs.buildPythonPackage rec {
  pname = "sqlcipher3-wheels";
  version = "0.5.2.post1";
  format = "setuptools";

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-PN6wYDI2xNy4OzWRd8ypzbN8T0fSWABhRLbWueHfc48=";
  };

  nativeBuildInputs = with python3.pkgs; [
    conan
    setuptools-scm
    pdm-backend
    wheel
  ];

  buildInputs = [ sqlcipher openssl conan ];

  pythonImportsCheck = [ "pysqlcipher3" ];

  meta = with lib; {
    description = "NOTICE: This is a fork of sqlcipher3 which adds github action for creating wheels for Windows, MacOS and Linux.";
    homepage = "https://github.com/laggykiller/sqlcipher3";
    license = licenses.zlib;
    maintainers = [ ];
  };
}
