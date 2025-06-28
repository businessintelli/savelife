import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  Brain, 
  Shield, 
  Upload, 
  DollarSign, 
  Calendar, 
  FileText, 
  Heart,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Users,
  Target
} from 'lucide-react'

const CampaignForm = () => {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    goal: '',
    description: '',
    medicalCondition: '',
    treatmentPlan: '',
    urgency: '',
    documents: []
  })

  const [aiSuggestions, setAiSuggestions] = useState({
    title: "Help [Name] Fight [Condition] - Every Dollar Counts",
    goalAmount: "$75,000",
    storyFramework: "Medical Journey Framework recommended based on your condition"
  })

  const totalSteps = 4
  const progress = (currentStep / totalSteps) * 100

  const medicalCategories = [
    "Cancer Treatment",
    "Emergency Surgery", 
    "Pediatric Care",
    "Mental Health",
    "Chronic Illness",
    "Accident Recovery",
    "Organ Transplant",
    "Rare Disease",
    "Rehabilitation",
    "Other"
  ]

  const urgencyLevels = [
    { value: "immediate", label: "Immediate (Within 1 week)", color: "red" },
    { value: "urgent", label: "Urgent (Within 1 month)", color: "orange" },
    { value: "planned", label: "Planned Treatment", color: "blue" }
  ]

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <Brain className="h-12 w-12 text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Campaign Basics</h2>
        <p className="text-gray-600">Let's start with the essential information about your campaign</p>
      </div>

      <div className="space-y-4">
        <div>
          <Label htmlFor="title" className="text-sm font-medium text-gray-700">Campaign Title</Label>
          <Input
            id="title"
            placeholder="Enter a compelling title for your campaign"
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            className="mt-1"
          />
          <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start">
              <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-blue-800">AI Suggestion</p>
                <p className="text-sm text-blue-700">{aiSuggestions.title}</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <Label htmlFor="category" className="text-sm font-medium text-gray-700">Medical Category</Label>
          <Select onValueChange={(value) => handleInputChange('category', value)}>
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Select the medical category" />
            </SelectTrigger>
            <SelectContent>
              {medicalCategories.map((category) => (
                <SelectItem key={category} value={category.toLowerCase().replace(' ', '-')}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="goal" className="text-sm font-medium text-gray-700">Funding Goal</Label>
          <div className="relative mt-1">
            <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              id="goal"
              type="number"
              placeholder="0"
              value={formData.goal}
              onChange={(e) => handleInputChange('goal', e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start">
              <Target className="h-4 w-4 text-green-600 mt-0.5 mr-2 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-green-800">AI Recommendation</p>
                <p className="text-sm text-green-700">Based on similar campaigns: {aiSuggestions.goalAmount}</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <Label htmlFor="urgency" className="text-sm font-medium text-gray-700">Treatment Urgency</Label>
          <Select onValueChange={(value) => handleInputChange('urgency', value)}>
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Select treatment urgency" />
            </SelectTrigger>
            <SelectContent>
              {urgencyLevels.map((level) => (
                <SelectItem key={level.value} value={level.value}>
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-2 bg-${level.color}-500`}></div>
                    {level.label}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <FileText className="h-12 w-12 text-purple-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Story</h2>
        <p className="text-gray-600">Share your story with our AI-powered writing assistant</p>
      </div>

      <div className="space-y-4">
        <div>
          <Label htmlFor="medicalCondition" className="text-sm font-medium text-gray-700">Medical Condition</Label>
          <Textarea
            id="medicalCondition"
            placeholder="Describe the medical condition or situation"
            value={formData.medicalCondition}
            onChange={(e) => handleInputChange('medicalCondition', e.target.value)}
            className="mt-1 min-h-[100px]"
          />
        </div>

        <div>
          <Label htmlFor="treatmentPlan" className="text-sm font-medium text-gray-700">Treatment Plan</Label>
          <Textarea
            id="treatmentPlan"
            placeholder="Describe the required treatment and associated costs"
            value={formData.treatmentPlan}
            onChange={(e) => handleInputChange('treatmentPlan', e.target.value)}
            className="mt-1 min-h-[100px]"
          />
        </div>

        <div>
          <Label htmlFor="description" className="text-sm font-medium text-gray-700">Campaign Description</Label>
          <Textarea
            id="description"
            placeholder="Tell your story - our AI will help optimize it for maximum impact"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            className="mt-1 min-h-[150px]"
          />
        </div>

        <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
          <div className="flex items-start">
            <Brain className="h-5 w-5 text-purple-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-purple-800 mb-2">AI Story Framework</p>
              <p className="text-sm text-purple-700 mb-3">{aiSuggestions.storyFramework}</p>
              <Button size="sm" variant="outline" className="border-purple-300 text-purple-700 hover:bg-purple-100">
                Get AI Writing Help
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <Shield className="h-12 w-12 text-green-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Documents</h2>
        <p className="text-gray-600">Upload documents for AI-powered verification while protecting your privacy</p>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="border-dashed border-2 border-gray-300 hover:border-blue-400 transition-colors">
            <CardContent className="p-6 text-center">
              <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-gray-700 mb-1">Medical Records</p>
              <p className="text-xs text-gray-500">Diagnosis, treatment plans, bills</p>
              <Button size="sm" variant="outline" className="mt-3">
                Upload Files
              </Button>
            </CardContent>
          </Card>

          <Card className="border-dashed border-2 border-gray-300 hover:border-blue-400 transition-colors">
            <CardContent className="p-6 text-center">
              <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-gray-700 mb-1">Insurance Documents</p>
              <p className="text-xs text-gray-500">Coverage details, claim denials</p>
              <Button size="sm" variant="outline" className="mt-3">
                Upload Files
              </Button>
            </CardContent>
          </Card>

          <Card className="border-dashed border-2 border-gray-300 hover:border-blue-400 transition-colors">
            <CardContent className="p-6 text-center">
              <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-gray-700 mb-1">Identity Verification</p>
              <p className="text-xs text-gray-500">Government ID, proof of address</p>
              <Button size="sm" variant="outline" className="mt-3">
                Upload Files
              </Button>
            </CardContent>
          </Card>

          <Card className="border-dashed border-2 border-gray-300 hover:border-blue-400 transition-colors">
            <CardContent className="p-6 text-center">
              <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-gray-700 mb-1">Financial Information</p>
              <p className="text-xs text-gray-500">Income verification, expenses</p>
              <Button size="sm" variant="outline" className="mt-3">
                Upload Files
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-start">
            <Shield className="h-5 w-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-green-800 mb-2">Privacy Protection</p>
              <p className="text-sm text-green-700 mb-2">
                Our AI analyzes your documents without storing sensitive details. Only verification status is shared publicly.
              </p>
              <Badge className="bg-green-100 text-green-800 border-green-200">
                <CheckCircle className="h-3 w-3 mr-1" />
                HIPAA Compliant
              </Badge>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <Heart className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Review & Launch</h2>
        <p className="text-gray-600">Review your campaign before launching to the world</p>
      </div>

      <Card className="border-0 shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{formData.title || "Your Campaign Title"}</CardTitle>
            <Badge className="bg-blue-100 text-blue-800 border-blue-200">
              {formData.category || "Category"}
            </Badge>
          </div>
          <CardDescription>
            Goal: ${formData.goal ? parseInt(formData.goal).toLocaleString() : "0"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Campaign Description</h4>
              <p className="text-gray-600 text-sm">
                {formData.description || "Your campaign description will appear here..."}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              <div className="text-center">
                <Users className="h-6 w-6 text-blue-600 mx-auto mb-1" />
                <p className="text-sm font-medium text-gray-900">Expected Reach</p>
                <p className="text-sm text-gray-600">2,500+ potential donors</p>
              </div>
              <div className="text-center">
                <Target className="h-6 w-6 text-green-600 mx-auto mb-1" />
                <p className="text-sm font-medium text-gray-900">Success Probability</p>
                <p className="text-sm text-gray-600">75% (AI Prediction)</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-yellow-800 mb-1">Before You Launch</p>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Your campaign will be reviewed within 24 hours</li>
              <li>• AI verification will process your documents securely</li>
              <li>• You'll receive optimization suggestions after launch</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Progress Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">Create Your Campaign</h1>
            <Badge className="bg-blue-100 text-blue-800 border-blue-200">
              Step {currentStep} of {totalSteps}
            </Badge>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Form Content */}
        <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm">
          <CardContent className="p-8">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
            {currentStep === 4 && renderStep4()}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-8 border-t border-gray-200 mt-8">
              <Button
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 1}
                className="border-gray-300 text-gray-700"
              >
                Previous
              </Button>
              
              {currentStep < totalSteps ? (
                <Button
                  onClick={nextStep}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Continue
                </Button>
              ) : (
                <Button className="bg-green-600 hover:bg-green-700 text-white">
                  Launch Campaign
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default CampaignForm

