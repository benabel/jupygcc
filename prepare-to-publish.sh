#!/bin/bash -
#===============================================================================
# Change la version dans le package.json
# Créé un tag v...
# Pousse vers github ou l'action de release sera lancée
#===============================================================================

set -o nounset                              # Treat unset variables as an error

uv tool run check
uv tool run format

echo "================"
echo "Version actuelle"
echo $(hatch version)
echo
echo "Nouvelle version souhaitée? "
read -p "major?minor?fix: " UP_TYPE

read -p "Etes vous sur: OUI?    " rep

if [ $rep != "OUI" ]
then
        echo "Abort release"
else
    echo "Lancement de la release"
    hatch version ${UP_TYPE}
    NEW_VERSION=$(hatch version)
    git commit -am "Publish v$NEW_VERSION"
    # Créer un tag pour la nouvelle version
    git tag v$NEW_VERSION

    # Pousser les changements et le tag vers le dépôt distant
    git push origin main  # Remplacez 'main' par le nom de votre branche
    git push origin v$NEW_VERSION
fi
