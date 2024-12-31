import React from 'react';

const Boutique = () => {
  return (
    <div className="min-h-screen text-white" style={{
      backgroundImage: "url('Capture d’écran 2024-11-26 124156.png')",
      backgroundSize: "cover",
      backgroundPosition: "center"
    }}>
      
      <main className="px-32 py-28">
        <h1 className="text-5xl font-lastica text-center mb-32">BIENVENUE DANS LA BOUTIQUE</h1>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-24">
          <div>
            <img src="Capture d’écran 2024-11-25 155102.png" alt="Produit 1" className="w-96 h-72 object-cover rounded-3xl" />
            <div className="mt-4">
              <h2 className="text-xl font-semibold text-white">Bandai - Jouet Cavalieri dello</h2>
              <p className="text-lg mt-2 text-[#c448d7]">OFFRE DE DÉPART : 1 ALGO</p>
              <button className="mt-4 px-6 py-2 bg-black rounded-full text-white hover:bg-gray-800">Acheter</button>
            </div>
          </div>

          <div>
            <img src="Capture d’écran 2024-11-25 155102.png" alt="Produit 2" className="w-96 h-72 object-cover rounded-3xl" />
            <div className="mt-4">
              <h2 className="text-xl font-semibold text-white">Bandai - Jouet Cavalieri dello</h2>
              <p className="text-lg mt-2 text-[#c448d7]">OFFRE DE DÉPART : 1 ALGO</p>
              <button className="mt-4 px-6 py-2 bg-black rounded-full text-white hover:bg-gray-800">Acheter</button>
            </div>
          </div>

          <div>
            <img src="Capture d’écran 2024-11-25 155102.png" alt="Produit 3" className="w-96 h-72 object-cover rounded-3xl" />
            <div className="mt-4">
              <h2 className="text-xl font-semibold text-white">Bandai - Jouet Cavalieri dello</h2>
              <p className="text-lg mt-2 text-[#c448d7]">OFFRE DE DÉPART : 1 ALGO</p>
              <button className="mt-4 px-6 py-2 bg-black rounded-full text-white hover:bg-gray-800">Acheter</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Boutique;
