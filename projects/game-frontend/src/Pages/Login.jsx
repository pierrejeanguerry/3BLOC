import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();  

  const handleSubmit = (event) => {
    event.preventDefault();
    
    navigate('/home');  
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <div className="max-w-md w-full flex">
        <div className="flex-1 p-8 bg-white shadow-lg rounded-md mr-4">
          <h1 className="text-3xl font-semibold mb-6">Se connecter</h1>
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="email" className="block text-gray-700">Email</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:border-blue-400"
                required
              />
            </div>
            <div className="mb-4">
              <label htmlFor="password" className="block text-gray-700">Mot de passe</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:border-blue-400"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-[#c448d7] text-white py-2 px-4 rounded-md hover:bg-pink-600 focus:outline-none focus:bg-blue-600"
            >
              Se connecter
            </button>
          </form>
          <p className="mt-4 text-center text-blue-500">
            <a href="/sign">Créer un compte</a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
