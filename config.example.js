// 🔒 EXAMPLE CONFIGURATION FILE
// Copy this file to config.js and add your actual values
// NEVER commit config.js to version control!

window.AvatarConfig = {
  // 🤖 HeyGen Configuration
  heygen: {
    // Get these from HeyGen dashboard - KEEP SECURE!
    // Use GitHub Secrets for deployment: HEYGEN_API_KEY
    apiKey: process.env.HEYGEN_API_KEY || 'your-heygen-api-key-here',
    avatarId: 'your-avatar-id-here',
    // Public settings (safe to commit)
    quality: 'high',
    autoStart: false,
    showControls: true
  },
  
  // 📊 Analytics (if needed)
  analytics: {
    // Use GitHub Secrets: GA_TRACKING_ID
    googleAnalyticsId: process.env.GA_TRACKING_ID || '',
    // Enable/disable tracking
    enabled: false
  },
  
  // 🎨 UI Configuration (safe to commit)
  ui: {
    theme: 'professional',
    headerTitle: 'Davide Consiglio',
    subtitle: 'Country Data Officer • Data & AI Strategy Expert',
    showAvatar: true,
    avatarPosition: 'bottom-right'
  },
  
  // 🔧 Feature Flags (safe to commit)
  features: {
    chatEnabled: true,
    timelineAnimation: true,
    skillsFilter: true,
    darkMode: false
  }
};

// 🛡️ Security Notes:
// 1. Never commit actual API keys
// 2. Use environment variables in production
// 3. Validate all inputs
// 4. Implement rate limiting
// 5. Use HTTPS only 