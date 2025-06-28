import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { 
  Search, 
  Filter, 
  Heart, 
  Users, 
  Clock, 
  CheckCircle, 
  MapPin,
  DollarSign,
  TrendingUp,
  Star,
  Share2,
  Bookmark
} from 'lucide-react'

const BrowseCampaigns = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedUrgency, setSelectedUrgency] = useState('all')
  const [sortBy, setSortBy] = useState('trending')

  const campaigns = [
    {
      id: 1,
      title: "Help Sarah's Daughter Fight Rare Disease",
      description: "8-year-old Emma needs specialized treatment for a rare genetic condition. Every donation brings us closer to giving her a normal childhood.",
      raised: 45000,
      goal: 150000,
      donors: 234,
      daysLeft: 45,
      location: "Austin, TX",
      verified: true,
      category: "Pediatric Care",
      urgency: "urgent",
      trending: true,
      aiMatch: 92,
      lastUpdate: "2 hours ago"
    },
    {
      id: 2,
      title: "Cancer Treatment for Local Teacher",
      description: "Mr. Johnson has dedicated 20 years to teaching our children. Now he needs our help to fight cancer and return to the classroom.",
      raised: 78000,
      goal: 120000,
      donors: 456,
      daysLeft: 32,
      location: "Denver, CO",
      verified: true,
      category: "Cancer Treatment",
      urgency: "immediate",
      trending: false,
      aiMatch: 87,
      lastUpdate: "5 hours ago"
    },
    {
      id: 3,
      title: "Emergency Surgery for Single Mom",
      description: "Maria needs urgent heart surgery to continue caring for her three children. Your support can save a life and keep a family together.",
      raised: 23000,
      goal: 85000,
      donors: 189,
      daysLeft: 28,
      location: "Phoenix, AZ",
      verified: true,
      category: "Emergency Care",
      urgency: "immediate",
      trending: true,
      aiMatch: 95,
      lastUpdate: "1 hour ago"
    },
    {
      id: 4,
      title: "Rehabilitation After Accident",
      description: "Young athlete needs extensive rehabilitation after a car accident to walk again and pursue his dreams.",
      raised: 34000,
      goal: 95000,
      donors: 167,
      daysLeft: 52,
      location: "Seattle, WA",
      verified: true,
      category: "Accident Recovery",
      urgency: "planned",
      trending: false,
      aiMatch: 78,
      lastUpdate: "3 hours ago"
    },
    {
      id: 5,
      title: "Mental Health Treatment for Veteran",
      description: "Supporting our hero's journey to mental wellness after years of service. Every contribution helps heal invisible wounds.",
      raised: 12000,
      goal: 45000,
      donors: 89,
      daysLeft: 38,
      location: "Nashville, TN",
      verified: true,
      category: "Mental Health",
      urgency: "urgent",
      trending: false,
      aiMatch: 83,
      lastUpdate: "4 hours ago"
    },
    {
      id: 6,
      title: "Organ Transplant for Father of Three",
      description: "David needs a kidney transplant to continue being there for his family. Time is running out, but hope remains strong.",
      raised: 67000,
      goal: 180000,
      donors: 312,
      daysLeft: 21,
      location: "Miami, FL",
      verified: true,
      category: "Organ Transplant",
      urgency: "immediate",
      trending: true,
      aiMatch: 91,
      lastUpdate: "30 minutes ago"
    }
  ]

  const categories = [
    "All Categories",
    "Cancer Treatment",
    "Pediatric Care", 
    "Emergency Care",
    "Mental Health",
    "Accident Recovery",
    "Organ Transplant",
    "Chronic Illness",
    "Rare Disease"
  ]

  const urgencyLevels = [
    { value: "all", label: "All Urgency Levels" },
    { value: "immediate", label: "Immediate", color: "red" },
    { value: "urgent", label: "Urgent", color: "orange" },
    { value: "planned", label: "Planned", color: "blue" }
  ]

  const sortOptions = [
    { value: "trending", label: "Trending" },
    { value: "newest", label: "Newest" },
    { value: "ending-soon", label: "Ending Soon" },
    { value: "most-funded", label: "Most Funded" },
    { value: "ai-match", label: "Best Match for You" }
  ]

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'immediate': return 'bg-red-100 text-red-800 border-red-200'
      case 'urgent': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'planned': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         campaign.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || 
                           campaign.category.toLowerCase().replace(' ', '-') === selectedCategory
    const matchesUrgency = selectedUrgency === 'all' || campaign.urgency === selectedUrgency
    
    return matchesSearch && matchesCategory && matchesUrgency
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Browse Campaigns</h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover meaningful campaigns and make a difference in someone's life. 
              Our AI helps you find causes that match your interests and values.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="mb-8">
          <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="lg:col-span-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search campaigns..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem 
                        key={category} 
                        value={category === "All Categories" ? "all" : category.toLowerCase().replace(' ', '-')}
                      >
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={selectedUrgency} onValueChange={setSelectedUrgency}>
                  <SelectTrigger>
                    <SelectValue placeholder="Urgency" />
                  </SelectTrigger>
                  <SelectContent>
                    {urgencyLevels.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        {level.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    {sortOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Results Summary */}
        <div className="mb-6 flex items-center justify-between">
          <p className="text-gray-600">
            Showing {filteredCampaigns.length} campaigns
            {sortBy === 'ai-match' && (
              <Badge className="ml-2 bg-purple-100 text-purple-800 border-purple-200">
                <Star className="h-3 w-3 mr-1" />
                AI Matched
              </Badge>
            )}
          </p>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-500">
              {searchTerm && `"${searchTerm}" • `}
              {selectedCategory !== 'all' && `${categories.find(c => c.toLowerCase().replace(' ', '-') === selectedCategory)} • `}
              {selectedUrgency !== 'all' && `${urgencyLevels.find(u => u.value === selectedUrgency)?.label}`}
            </span>
          </div>
        </div>

        {/* Campaign Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCampaigns.map((campaign) => (
            <Card key={campaign.id} className="overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white group">
              {/* Campaign Image Placeholder */}
              <div className="aspect-video bg-gradient-to-br from-blue-100 to-green-100 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <Heart className="h-16 w-16 text-blue-300" />
                </div>
                
                {/* Badges */}
                <div className="absolute top-3 left-3 flex flex-col space-y-2">
                  {campaign.verified && (
                    <Badge className="bg-green-100 text-green-800 border-green-200">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Verified
                    </Badge>
                  )}
                  <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                    {campaign.category}
                  </Badge>
                </div>

                <div className="absolute top-3 right-3 flex flex-col space-y-2">
                  {campaign.trending && (
                    <Badge className="bg-orange-100 text-orange-800 border-orange-200">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      Trending
                    </Badge>
                  )}
                  <Badge className={getUrgencyColor(campaign.urgency)}>
                    {campaign.urgency}
                  </Badge>
                </div>

                {/* Action Buttons */}
                <div className="absolute bottom-3 right-3 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button size="sm" variant="secondary" className="bg-white/80 backdrop-blur-sm">
                    <Share2 className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="secondary" className="bg-white/80 backdrop-blur-sm">
                    <Bookmark className="h-3 w-3" />
                  </Button>
                </div>
              </div>

              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg font-semibold text-gray-900 line-clamp-2 flex-1">
                    {campaign.title}
                  </CardTitle>
                  {sortBy === 'ai-match' && (
                    <Badge className="ml-2 bg-purple-100 text-purple-800 border-purple-200 flex-shrink-0">
                      {campaign.aiMatch}% match
                    </Badge>
                  )}
                </div>
                <CardDescription className="text-gray-600 line-clamp-3">
                  {campaign.description}
                </CardDescription>
                <div className="flex items-center text-sm text-gray-500 mt-2">
                  <MapPin className="h-3 w-3 mr-1" />
                  {campaign.location}
                  <span className="mx-2">•</span>
                  <Clock className="h-3 w-3 mr-1" />
                  Updated {campaign.lastUpdate}
                </div>
              </CardHeader>

              <CardContent className="pt-0">
                <div className="space-y-4">
                  {/* Progress */}
                  <div>
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>${campaign.raised.toLocaleString()} raised</span>
                      <span>${campaign.goal.toLocaleString()} goal</span>
                    </div>
                    <Progress value={(campaign.raised / campaign.goal) * 100} className="h-2" />
                    <div className="text-xs text-gray-500 mt-1">
                      {Math.round((campaign.raised / campaign.goal) * 100)}% funded
                    </div>
                  </div>
                  
                  {/* Stats */}
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
                  
                  {/* Action Buttons */}
                  <div className="flex space-x-2 pt-2">
                    <Button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white">
                      <DollarSign className="h-4 w-4 mr-1" />
                      Donate
                    </Button>
                    <Button variant="outline" className="border-gray-300 text-gray-700">
                      Learn More
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Load More */}
        <div className="text-center mt-12">
          <Button variant="outline" size="lg" className="border-gray-300 text-gray-700">
            Load More Campaigns
          </Button>
        </div>
      </div>
    </div>
  )
}

export default BrowseCampaigns

