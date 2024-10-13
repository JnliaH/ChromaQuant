echo "[ChromaQuant Bundle] Bundling app using Pyinstaller..."
pyinstaller ChromaQuantBinary.spec
echo "[ChromaQuant Bundle] App bundled."
echo "[ChromaQuant Bundle] Updating permissions of distribution"
chmod ugo=rwx ./dist/ChromaQuantBinary
echo "[ChromaQuant Bundle] Permissions updated"
echo "[ChromaQuant Bundle] Copying files to distribution directory..."
echo "[ChromaQuant Bundle] Copying AutoFpmMatch.py ..."
cp AutoFpmMatch.py ./dist/ChromaQuantBinary
echo "[ChromaQuant Bundle] Copying AutoQuantification.py ..."
cp AutoQuantification.py ./dist/ChromaQuantBinary
echo "[ChromaQuant Bundle] Copying handleDirectories.py ..."
cp handleDirectories.py ./dist/ChromaQuantBinary/_internal
echo "[ChromaQuant Bundle] Copying README.md, LICENSES.txt, and LICENSES_bundled.txt ..."
cp README.md ./dist/ChromaQuantBinary
cp LICENSE.txt ./dist/ChromaQuantBinary
cp LICENSES_bundled.txt ./dist/ChromaQuantBinary
echo "[ChromaQuant Bundle] Files copied"