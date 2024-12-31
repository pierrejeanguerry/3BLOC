import React from 'react';

const Actifs = () => {
  const assets = [
    {
      name: "Épée Légendaire",
      image: "Capture d’écran 2024-11-25 155102.png",
      properties: "+50 dégâts, +20 agilité",
      date: "15 Novembre 2024",
    },
    {
      name: "Arc Mystique",
      image: "Capture d’écran 2024-11-25 155102.png",
      properties: "+40 dégâts, +15 précision",
      date: "20 Octobre 2024",
    },
    {
      name: "Bouclier Ancestral",
      image: "Capture d’écran 2024-11-25 155102.png",
      properties: "+70 défense, +10 résistance",
      date: "5 Septembre 2024",
    },
  ];

  return (
    <div
      className="min-h-screen text-white"
      style={{
        backgroundImage: "url('Capture d’écran 2024-11-26 124156.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <main className="px-32 py-28">
        <h1 className="text-5xl font-lastica text-center mb-32">Vos Actifs</h1>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-24">
          {assets.map((asset, index) => (
            <div
              key={index}
              className="bg-gray-800 bg-opacity-75 p-6 rounded-3xl shadow-xl"
            >
              <img
                src={asset.image}
                alt={asset.name}
                className="w-full h-48 object-cover rounded-lg mb-4"
              />
              <h2 className="text-3xl font-lastica mb-4">{asset.name}</h2>
              <p className="text-lg mb-2">
                <strong>Propriétés :</strong> {asset.properties}
              </p>
              <p className="text-lg mb-2">
                <strong>Date d'acquisition :</strong> {asset.date}
              </p>
              <button className="mt-4 px-6 py-3 bg-[#c448d7] text-white rounded-full hover:bg-pink-600">
                Revendre
              </button>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default Actifs;
