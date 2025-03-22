
// components/UserRegistration.tsx
import React, { useState } from 'react';

interface UserFormData {
  username: string;
  password: string;
  birthyear: number;
  gender: string;
  country: string;
  state: string;
  city: string;
}

export const UserRegistration: React.FC = () => {
  const [formData, setFormData] = useState<UserFormData>({
    username: '',
    password: '',
    birthyear: new Date().getFullYear() - 25,
    gender: '',
    country: '',
    state: '',
    city: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'birthyear' ? parseInt(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage({ text: '', type: '' });

    try {
      // Format the data according to the API requirements
      const userData = {
        username: formData.username,
        password: formData.password,
        birthyear: formData.birthyear,
        gender: formData.gender,
        location: {
          country: formData.country,
          state: formData.state,
          city: formData.city
        }
      };

      const response = await fetch('/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const result = await response.json();
      
      if (response.ok) {
        setMessage({ text: 'Registration successful!', type: 'success' });
        // Reset form after successful registration
        setFormData({
          username: '',
          password: '',
          birthyear: new Date().getFullYear() - 25,
          gender: '',
          country: '',
          state: '',
          city: ''
        });
      } else {
        setMessage({ text: result.message || 'Registration failed', type: 'error' });
      }
    } catch (error) {
      setMessage({ text: 'An error occurred. Please try again.', type: 'error' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-center">User Registration</h2>
      
      {message.text && (
        <div className={`p-4 mb-4 rounded ${message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {message.text}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Birth Year</label>
            <input
              type="number"
              name="birthyear"
              value={formData.birthyear}
              onChange={handleChange}
              required
              min="1900"
              max={new Date().getFullYear()}
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              required
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="">Select Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="non-binary">Non-binary</option>
              <option value="prefer-not-to-say">Prefer not to say</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
            <input
              type="text"
              name="country"
              value={formData.country}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">State/Province</label>
            <input
              type="text"
              name="state"
              value={formData.state}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
            <input
              type="text"
              name="city"
              value={formData.city}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
        
        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-6 w-full bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-md font-medium disabled:opacity-50"
        >
          {isSubmitting ? 'Registering...' : 'Register Account'}
        </button>
      </form>
    </div>
  );
};
