import React from 'react';

const Home = () => {
  const username = "NomUtilisateur";

  return (
    <div className="min-h-screen text-white" style={{
      backgroundImage: "url('Capture d’écran 2024-11-26 124156.png')",
      backgroundSize: "cover",
      backgroundPosition: "center"
    }}>
      <main className="px-32 py-16">
        <h1 className="text-5xl font-belleza text-center mb-16 uppercase">
          Bienvenue, <span>{username}</span>
        </h1>

        <section className="bg-black bg-opacity-70 rounded-3xl p-8 mb-16">
          <h2 className="text-3xl font-semibold mb-6">Solde Actuel</h2>
          <p className="text-4xl font-bold text-[#c448d7]">150 ALGO</p>
        </section>

        <section className="bg-black bg-opacity-70 rounded-3xl p-8">
          <h2 className="text-3xl font-semibold mb-6">Transactions Récentes</h2>
          <table className="w-full text-left text-white">
            <thead>
              <tr>
                <th className="border-b border-gray-600 py-4 px-4">Date</th>
                <th className="border-b border-gray-600 py-4 px-4">Description</th>
                <th className="border-b border-gray-600 py-4 px-4">Montant</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border-b border-gray-600 py-4 px-4">26/11/2024</td>
                <td className="border-b border-gray-600 py-4 px-4">Achat Jouet Virtuel</td>
                <td className="border-b border-gray-600 py-4 px-4 text-[#c448d7]">-10 ALGO</td>
              </tr>
              <tr>
                <td className="border-b border-gray-600 py-4 px-4">25/11/2024</td>
                <td className="border-b border-gray-600 py-4 px-4">Vente Actif Numérique</td>
                <td className="border-b border-gray-600 py-4 px-4 text-[#4CAF50]">+20 ALGO</td>
              </tr>
              <tr>
                <td className="border-b border-gray-600 py-4 px-4">24/11/2024</td>
                <td className="border-b border-gray-600 py-4 px-4">Recharge de Portefeuille</td>
                <td className="border-b border-gray-600 py-4 px-4 text-[#4CAF50]">+100 ALGO</td>
              </tr>
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
};

export default Home;
