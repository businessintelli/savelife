# SaveLife.com - AI-Powered Medical Crowdfunding Platform

[![Deploy to AWS](https://github.com/savelife/savelife/actions/workflows/deploy-aws.yml/badge.svg)](https://github.com/savelife/savelife/actions/workflows/deploy-aws.yml)
[![Deploy to GCP](https://github.com/savelife/savelife/actions/workflows/deploy-gcp.yml/badge.svg)](https://github.com/savelife/savelife/actions/workflows/deploy-gcp.yml)
[![Deploy to Azure](https://github.com/savelife/savelife/actions/workflows/deploy-azure.yml/badge.svg)](https://github.com/savelife/savelife/actions/workflows/deploy-azure.yml)

SaveLife.com is a revolutionary AI-powered medical crowdfunding platform that combines cutting-edge artificial intelligence with compassionate human-centered design to help patients and families raise funds for life-saving medical treatments.

## 🌟 Features

- **AI-Powered Campaign Creation** - Intelligent assistance for creating compelling fundraising campaigns
- **Automated Verification** - AI-driven document verification and fraud detection
- **Personalized Donor Matching** - Smart algorithms that connect donors with relevant campaigns
- **HIPAA Compliant** - Secure handling of sensitive medical information
- **Multi-Cloud Deployment** - Support for AWS, GCP, and Azure deployments
- **Responsive Design** - Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

```
savelife/
├── frontend/                 # React web application
├── backend/                  # Flask AI services backend
├── infrastructure/           # Cloud deployment configurations
│   ├── aws/                 # AWS CloudFormation templates
│   ├── gcp/                 # Google Cloud Deployment Manager
│   └── azure/               # Azure Resource Manager templates
├── .github/workflows/       # CI/CD pipeline configurations
├── docs/                    # Comprehensive documentation
├── assets/                  # Mobile mockups and design assets
└── tests/                   # Additional test files
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+ and pip
- Docker (optional)
- Cloud CLI tools (AWS CLI, gcloud, Azure CLI)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/savelife.git
   cd savelife
   ```

2. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python src/main.py
   ```

4. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

## ☁️ Cloud Deployment

### AWS Deployment

```bash
# Deploy to AWS using CloudFormation
cd infrastructure/aws
aws cloudformation deploy --template-file savelife-infrastructure.yml --stack-name savelife-prod --capabilities CAPABILITY_IAM
```

### Google Cloud Deployment

```bash
# Deploy to GCP using Deployment Manager
cd infrastructure/gcp
gcloud deployment-manager deployments create savelife-prod --config savelife-infrastructure.yaml
```

### Azure Deployment

```bash
# Deploy to Azure using ARM templates
cd infrastructure/azure
az deployment group create --resource-group savelife-rg --template-file savelife-infrastructure.json
```

## 🔄 CI/CD Pipeline

The repository includes automated CI/CD pipelines for all three cloud providers:

- **GitHub Actions** - Automated testing and deployment
- **Multi-Cloud Support** - Deploy to AWS, GCP, and Azure simultaneously
- **Environment Management** - Separate staging and production environments
- **Automated Testing** - Unit, integration, and end-to-end tests
- **Security Scanning** - Automated vulnerability and compliance checks

### Pipeline Triggers

- **Push to main** - Deploys to production
- **Pull requests** - Runs tests and deploys to staging
- **Manual triggers** - On-demand deployments

## 🧪 Testing

### Frontend Testing
```bash
cd frontend
npm test                    # Unit tests
npm run test:e2e           # End-to-end tests
npm run test:coverage      # Coverage report
```

### Backend Testing
```bash
cd backend
source venv/bin/activate
pytest                     # Run all tests
pytest --cov              # Coverage report
```

## 📚 Documentation

- [User Guide](docs/savelife_user_guide.md) - Complete user documentation
- [Deployment Guide](docs/savelife_deployment_guide.md) - Operations and maintenance
- [API Documentation](docs/savelife_ai_integration_guide.md) - Developer resources
- [Architecture Overview](docs/savelife_ai_architecture.md) - Technical specifications
- [Project Summary](docs/savelife_project_summary.md) - Executive overview

## 🔒 Security

- **HIPAA Compliance** - Secure handling of protected health information
- **Data Encryption** - End-to-end encryption for sensitive data
- **Access Controls** - Role-based permissions and authentication
- **Audit Logging** - Comprehensive activity tracking
- **Security Scanning** - Automated vulnerability assessments

## 🤖 AI Services

### Campaign AI
- Intelligent title and goal recommendations
- Real-time writing assistance
- Campaign optimization suggestions
- Medical condition analysis

### Verification AI
- Automated document analysis
- Fraud detection algorithms
- Trust scoring system
- HIPAA-compliant processing

### Donor Matching AI
- Personalized campaign recommendations
- Behavioral analysis and profiling
- Optimal timing calculations
- Impact prediction modeling

## 🌍 Environment Variables

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:5000
VITE_STRIPE_PUBLIC_KEY=your_stripe_public_key
VITE_ANALYTICS_ID=your_analytics_id
```

### Backend (.env)
```
DATABASE_URL=sqlite:///savelife.db
SECRET_KEY=your_secret_key
STRIPE_SECRET_KEY=your_stripe_secret_key
AI_MODEL_API_KEY=your_ai_api_key
```

## 📊 Monitoring

- **Application Performance** - Real-time performance metrics
- **Error Tracking** - Automated error detection and alerting
- **User Analytics** - Campaign and donation tracking
- **Infrastructure Monitoring** - Cloud resource utilization
- **Security Monitoring** - Threat detection and response

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style and conventions
- Write comprehensive tests for new features
- Update documentation for any API changes
- Ensure all CI/CD checks pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation** - Check the [docs](docs/) directory
- **Issues** - Report bugs and feature requests via GitHub Issues
- **Discussions** - Join community discussions in GitHub Discussions
- **Email** - Contact support@savelife.com for urgent issues

## 🏆 Acknowledgments

- Built with ❤️ for patients and families facing medical crises
- Powered by advanced AI and machine learning technologies
- Designed with privacy, security, and compliance as top priorities
- Supported by a community of developers, healthcare professionals, and advocates

---

**Live Platform URLs:**
- **Production Web App:** https://ldefeujl.manus.space
- **AI Services API:** https://xlhyimcj6x0e.manus.space

**Project Status:** ✅ Complete and Operational

For detailed setup instructions and deployment guides, please refer to the documentation in the `docs/` directory.

