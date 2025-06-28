import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  Heart, 
  Shield, 
  Brain, 
  Users, 
  TrendingUp, 
  CheckCircle, 
  Star,
  ArrowRight,
  Search,
  Menu,
  X,
  DollarSign,
  Clock,
  Award,
  Zap
} from 'lucide-react'
import './App.css'

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const featuredCampaigns = [
    {
      id: 1,
      title: "Help Sarah's Daughter Fight Rare Disease",
      description: "8-year-old Emma needs specialized treatment for a rare genetic condition. Every donation brings us closer to giving her a normal childhood.",
      raised: 45000,
      goal: 150000,
      donors: 234,
      daysLeft: 45,
      image: "/api/placeholder/400/250",
      verified: true,
      category: "Pediatric Care"
    },
    {
      id: 2,
      title: "Cancer Treatment for Local Teacher",
      description: "Mr. Johnson has dedicated 20 years to teaching our children. Now he needs our help to fight cancer and return to the classroom.",
      raised: 78000,
      goal: 120000,
      donors: 456,
      daysLeft: 32,
      image: "/api/placeholder/400/250",
      verified: true,
      category: "Cancer Treatment"
    },
    {
      id: 3,
      title: "Emergency Surgery for Single Mom",
      description: "Maria needs urgent heart surgery to continue caring for her three children. Your support can save a life and keep a family together.",
      raised: 23000,
      goal: 85000,
      donors: 189,
      daysLeft: 28,
      image: "/api/placeholder/400/250",
      verified: true,
      category: "Emergency Care"
    }
  ]

  const features = [
    {
      icon: <Brain className="h-8 w-8 text-blue-600" />,
      title: "AI-Powered Campaign Creation",
      description: "Our intelligent system helps you craft compelling stories that connect with donors while maintaining your dignity and privacy."
    },
    {
      icon: <Shield className="h-8 w-8 text-green-600" />,
      title: "Verified Trust System",
      description: "Advanced verification ensures campaign authenticity while protecting sensitive medical information through HIPAA-compliant processes."
    },
    {
      icon: <Users className="h-8 w-8 text-purple-600" />,
      title: "Smart Donor Matching",
      description: "AI connects your campaign with potential donors who care about causes like yours, expanding reach beyond your social network."
    },
    {
      icon: <TrendingUp className="h-8 w-8 text-orange-600" />,
      title: "6x Higher Success Rate",
      description: "Our platform achieves 60% campaign success compared to 10% on traditional platforms through intelligent optimization."
    }
  ]

  const stats = [
    { label: "Campaigns Funded", value: "2,500+", icon: <CheckCircle className="h-6 w-6" /> },
    { label: "Lives Impacted", value: "15,000+", icon: <Heart className="h-6 w-6" /> },
    { label: "Funds Raised", value: "$45M+", icon: <DollarSign className="h-6 w-6" /> },
    { label: "Success Rate", value: "60%", icon: <Award className="h-6 w-6" /> }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <Heart className="h-8 w-8 text-blue-600 mr-2" />
                <span className="text-2xl font-bold text-gray-900">SaveLife</span>
                <span className="text-sm text-gray-500 ml-1">.com</span>
              </div>
            </div>
            
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-8">
                <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors">Browse Campaigns</a>
                <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors">How It Works</a>
                <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors">Success Stories</a>
                <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors">For Healthcare Providers</a>
              </div>
            </div>

            <div className="hidden md:flex items-center space-x-4">
              <Button variant="ghost" className="text-gray-700">Sign In</Button>
              <Button className="bg-blue-600 hover:bg-blue-700 text-white">Start Campaign</Button>
            </div>

            <div className="md:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a href="#" className="block px-3 py-2 text-gray-700 hover:text-blue-600">Browse Campaigns</a>
              <a href="#" className="block px-3 py-2 text-gray-700 hover:text-blue-600">How It Works</a>
              <a href="#" className="block px-3 py-2 text-gray-700 hover:text-blue-600">Success Stories</a>
              <a href="#" className="block px-3 py-2 text-gray-700 hover:text-blue-600">For Healthcare Providers</a>
              <div className="pt-4 pb-2 border-t border-gray-200 mt-4">
                <Button variant="ghost" className="w-full mb-2">Sign In</Button>
                <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">Start Campaign</Button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <Badge className="mb-4 bg-blue-100 text-blue-800 border-blue-200">
              <Zap className="h-4 w-4 mr-1" />
              AI-Powered Medical Crowdfunding
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Turn Medical Crises Into
              <span className="text-blue-600 block">Community Triumphs</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              SaveLife.com uses advanced AI to help you create compelling campaigns, verify authenticity, 
              and connect with donors who care. Achieve 6x higher success rates while maintaining your dignity and privacy.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3">
                Start Your Campaign
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="border-gray-300 text-gray-700 px-8 py-3">
                Browse Campaigns
                <Search className="ml-2 h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-2 text-blue-600">
                  {stat.icon}
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why SaveLife.com Works Better
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI-powered platform addresses the fundamental problems that cause 90% of medical campaigns to fail on traditional platforms.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white/80 backdrop-blur-sm">
                <CardHeader className="text-center pb-4">
                  <div className="flex justify-center mb-4">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-lg font-semibold text-gray-900">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600 text-center">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Campaigns */}
      <section className="py-20 bg-white/50 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Featured Campaigns
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Real people, real needs, real impact. See how our community comes together to support those in crisis.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredCampaigns.map((campaign) => (
              <Card key={campaign.id} className="overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white">
                <div className="aspect-video bg-gradient-to-br from-blue-100 to-green-100 relative">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Heart className="h-16 w-16 text-blue-300" />
                  </div>
                  {campaign.verified && (
                    <Badge className="absolute top-3 right-3 bg-green-100 text-green-800 border-green-200">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Verified
                    </Badge>
                  )}
                  <Badge className="absolute top-3 left-3 bg-blue-100 text-blue-800 border-blue-200">
                    {campaign.category}
                  </Badge>
                </div>
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-gray-900 line-clamp-2">
                    {campaign.title}
                  </CardTitle>
                  <CardDescription className="text-gray-600 line-clamp-3">
                    {campaign.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span>${campaign.raised.toLocaleString()} raised</span>
                        <span>${campaign.goal.toLocaleString()} goal</span>
                      </div>
                      <Progress value={(campaign.raised / campaign.goal) * 100} className="h-2" />
                    </div>
                    
                    <div className="flex justify-between text-sm text-gray-600">
                      <div className="flex items-center">
                        <Users className="h-4 w-4 mr-1" />
                        {campaign.donors} donors
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {campaign.daysLeft} days left
                      </div>
                    </div>
                    
                    <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                      Donate Now
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <Button variant="outline" size="lg" className="border-gray-300 text-gray-700">
              View All Campaigns
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-green-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Start Your Campaign?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands who have successfully raised funds for medical expenses with our AI-powered platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
              Start Campaign Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3">
              Learn How It Works
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-1">
              <div className="flex items-center mb-4">
                <Heart className="h-8 w-8 text-blue-400 mr-2" />
                <span className="text-2xl font-bold">SaveLife</span>
                <span className="text-sm text-gray-400 ml-1">.com</span>
              </div>
              <p className="text-gray-400 mb-4">
                AI-powered medical crowdfunding platform helping families access life-saving treatments.
              </p>
              <div className="flex space-x-4">
                <Star className="h-5 w-5 text-gray-400 hover:text-white cursor-pointer" />
                <Star className="h-5 w-5 text-gray-400 hover:text-white cursor-pointer" />
                <Star className="h-5 w-5 text-gray-400 hover:text-white cursor-pointer" />
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Platform</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Start Campaign</a></li>
                <li><a href="#" className="hover:text-white">Browse Campaigns</a></li>
                <li><a href="#" className="hover:text-white">How It Works</a></li>
                <li><a href="#" className="hover:text-white">Success Stories</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Contact Us</a></li>
                <li><a href="#" className="hover:text-white">Safety & Trust</a></li>
                <li><a href="#" className="hover:text-white">Healthcare Providers</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About Us</a></li>
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white">HIPAA Compliance</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; 2025 SaveLife.com. All rights reserved. HIPAA Compliant Medical Crowdfunding Platform.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

