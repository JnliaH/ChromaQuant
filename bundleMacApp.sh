echo "[ChromaQuant Bundle] Bundling app using Pyinstaller..."
pyinstaller ChromaQuantApp.spec
echo "[ChromaQuant Bundle] App bundled."
echo "[ChromaQuant Bundle] Copying files to distribution directory..."
echo "[ChromaQuant Bundle] Copying AutoFpmMatch.py ..."
cp AutoFpmMatch.py /dist
echo "[ChromaQuant Bundle] Copying AutoQuantification.py ..."
cp AutoQuantification.py /dist
echo "[ChromaQuant Bundle] Copying handleDirectories.py ..."
cp handleDirectories.py /dist/_internal
echo "[ChromaQuant Bundle] Copying README.md, LICENSES.txt, and LICENSES_bundled.txt ..."
cp README.md /dist
cp LICENSE.txt /dist
cp LICENSES_bundled.txt /dist
echo "[ChromaQuant Bundle] Files copied"