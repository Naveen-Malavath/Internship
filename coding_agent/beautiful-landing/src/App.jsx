import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const features = [
    {
      icon: '⚡',
      title: 'Lightning Fast',
      description: 'Optimized performance with cutting-edge technology for blazing speed.'
    },
    {
      icon: '🎨',
      title: 'Beautiful Design',
      description: 'Stunning visuals crafted with attention to every pixel and detail.'
    },
    {
      icon: '🚀',
      title: 'Easy to Use',
      description: 'Intuitive interface that makes complex tasks simple and enjoyable.'
    }
  ];

  return (
    <div className="App">
      {/* Hero Section */}
      <section className="hero">
        <div className="stars"></div>
        <div className="stars2"></div>
        <div className="stars3"></div>
        
        <div className="hero-content" style={{ transform: `translateY(${scrollY * 0.5}px)` }}>
          <h1 className="hero-title">
            Welcome to the
            <span className="gradient-text"> Future</span>
          </h1>
          <p className="hero-subtitle">
            Experience the next generation of digital innovation with stunning design and powerful features
          </p>
          <button className="cta-button">
            <span>Get Started</span>
            <div className="glow"></div>
          </button>
        </div>

        <div className="scroll-indicator">
          <div className="mouse">
            <div className="wheel"></div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2 className="section-title">Why Choose Us</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="feature-card"
              style={{ 
                animationDelay: `${index * 0.2}s`,
                transform: scrollY > 200 ? 'translateY(0) scale(1)' : 'translateY(50px) scale(0.9)',
                opacity: scrollY > 200 ? 1 : 0,
                transition: `all 0.6s ease ${index * 0.1}s`
              }}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <div className="feature-glow"></div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>© 2024 Beautiful Landing. Crafted with passion.</p>
      </footer>
    </div>
  )
}

export default App
