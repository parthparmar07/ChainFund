import { useState } from "react";
import { ArrowLeft, Upload, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { campaignsApi, CreateCampaignRequest, ApiError } from "@/services/api";
import { useWalletStore } from "@/stores/walletStore";

interface Milestone {
  id: string;
  title: string;
  description: string;
  amount: number;
}

export default function CreateCampaign() {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "",
    goal: "",
    duration: "",
    coverImage: null as File | null,
  });
  
  const [milestones, setMilestones] = useState<Milestone[]>([
    { id: "1", title: "", description: "", amount: 0 }
  ]);

  const steps = [
    { number: 1, title: "Basic Info", description: "Campaign details" },
    { number: 2, title: "Milestones", description: "Funding milestones" },
    { number: 3, title: "Review", description: "Final review" },
  ];

  const categories = [
    "Technology", "Health", "Environment", "Education", "Arts", "Social Impact"
  ];

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const addMilestone = () => {
    const newMilestone: Milestone = {
      id: Date.now().toString(),
      title: "",
      description: "",
      amount: 0,
    };
    setMilestones([...milestones, newMilestone]);
  };

  const removeMilestone = (id: string) => {
    if (milestones.length > 1) {
      setMilestones(milestones.filter(m => m.id !== id));
    }
  };

  const updateMilestone = (id: string, field: string, value: string | number) => {
    setMilestones(milestones.map(m => 
      m.id === id ? { ...m, [field]: value } : m
    ));
  };

  const handleSubmit = async () => {
    try {
      // Validate form
      if (!formData.title || !formData.description || !formData.goal) {
        toast({
          title: "Missing Information",
          description: "Please fill in all required fields.",
          variant: "destructive",
        });
        return;
      }

      if (milestones.length === 0) {
        toast({
          title: "No Milestones",
          description: "Please add at least one milestone to your campaign.",
          variant: "destructive",
        });
        return;
      }

      // Prepare campaign data
      const campaignData: CreateCampaignRequest = {
        title: formData.title,
        description: formData.description,
        goal_amount: parseFloat(formData.goal),
        category: formData.category || 'technology',
        duration_days: parseInt(formData.duration || '30'),
        milestones: milestones.map(m => ({
          title: m.title,
          description: m.description,
          amount: m.amount,
        })),
      };

      // Call API to create campaign
      await campaignsApi.createCampaign(campaignData);

      toast({
        title: "Campaign Created!",
        description: "Your campaign has been successfully created and will be reviewed.",
      });

      navigate("/dashboard");
    } catch (error) {
      console.error('Campaign creation failed:', error);
      toast({
        title: "Error",
        description: error instanceof ApiError ? error.message : "Failed to create campaign. Please try again.",
        variant: "destructive",
      });
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Campaign Title *</Label>
              <Input
                id="title"
                placeholder="Enter your campaign title"
                value={formData.title}
                onChange={(e) => handleInputChange("title", e.target.value)}
                className="glass"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                placeholder="Describe your project, goals, and impact..."
                value={formData.description}
                onChange={(e) => handleInputChange("description", e.target.value)}
                className="glass min-h-[120px]"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <select
                  id="category"
                  value={formData.category}
                  onChange={(e) => handleInputChange("category", e.target.value)}
                  className="w-full px-3 py-2 glass rounded-md border border-glass-border/20 focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">Select category</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat.toLowerCase()}>{cat}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="goal">Funding Goal (USD) *</Label>
                <Input
                  id="goal"
                  type="number"
                  placeholder="50000"
                  value={formData.goal}
                  onChange={(e) => handleInputChange("goal", e.target.value)}
                  className="glass"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="duration">Campaign Duration (days)</Label>
              <Input
                id="duration"
                type="number"
                placeholder="90"
                value={formData.duration}
                onChange={(e) => handleInputChange("duration", e.target.value)}
                className="glass"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="cover-image">Cover Image</Label>
              <div className="border-2 border-dashed border-glass-border/20 rounded-lg p-8 text-center glass">
                <Upload className="w-8 h-8 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground mb-2">
                  Drag and drop an image, or click to browse
                </p>
                <Button variant="outline" size="sm">
                  Choose File
                </Button>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">Set Up Milestones</h3>
              <p className="text-muted-foreground">
                Break down your funding into milestones. Funds are released as milestones are approved by backers.
              </p>
            </div>

            <div className="space-y-4">
              {milestones.map((milestone, index) => (
                <Card key={milestone.id} className="glass">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-center">
                      <CardTitle className="text-sm">Milestone {index + 1}</CardTitle>
                      {milestones.length > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeMilestone(milestone.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Milestone Title</Label>
                      <Input
                        placeholder="e.g., Prototype Development"
                        value={milestone.title}
                        onChange={(e) => updateMilestone(milestone.id, "title", e.target.value)}
                        className="glass"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Description</Label>
                      <Textarea
                        placeholder="Describe what will be achieved in this milestone..."
                        value={milestone.description}
                        onChange={(e) => updateMilestone(milestone.id, "description", e.target.value)}
                        className="glass"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>Funding Amount (USD)</Label>
                      <Input
                        type="number"
                        placeholder="10000"
                        value={milestone.amount || ""}
                        onChange={(e) => updateMilestone(milestone.id, "amount", parseFloat(e.target.value) || 0)}
                        className="glass"
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Button 
              variant="outline" 
              onClick={addMilestone}
              className="w-full"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Milestone
            </Button>

            <div className="glass rounded-lg p-4">
              <div className="flex justify-between text-sm">
                <span>Total Milestone Funding:</span>
                <span className="font-semibold">
                  ${milestones.reduce((sum, m) => sum + m.amount, 0).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between text-sm mt-2">
                <span>Campaign Goal:</span>
                <span className="font-semibold">${parseInt(formData.goal || "0").toLocaleString()}</span>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">Review Your Campaign</h3>
              <p className="text-muted-foreground">
                Review all details before creating your campaign.
              </p>
            </div>

            <Card className="glass">
              <CardHeader>
                <CardTitle>{formData.title}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">{formData.description}</p>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Category:</span>
                    <span className="ml-2 capitalize">{formData.category}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Goal:</span>
                    <span className="ml-2">${parseInt(formData.goal || "0").toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Duration:</span>
                    <span className="ml-2">{formData.duration} days</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Milestones:</span>
                    <span className="ml-2">{milestones.length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass">
              <CardHeader>
                <CardTitle className="text-lg">Milestones</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {milestones.map((milestone, index) => (
                    <div key={milestone.id} className="flex justify-between items-center p-3 bg-muted/20 rounded-lg">
                      <div>
                        <div className="font-medium">
                          {milestone.title || `Milestone ${index + 1}`}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {milestone.description}
                        </div>
                      </div>
                      <div className="text-primary font-semibold">
                        ${milestone.amount.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => navigate("/dashboard")}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>
        <div>
          <h1 className="text-3xl font-bold gradient-text">Create Campaign</h1>
          <p className="text-muted-foreground">Launch your project on the blockchain</p>
        </div>
      </div>

      {/* Progress Steps */}
      <Card className="glass">
        <CardContent className="p-6">
          <div className="flex justify-between items-center">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                  currentStep >= step.number 
                    ? 'bg-primary border-primary text-primary-foreground' 
                    : 'border-gray-500 text-gray-500'
                }`}>
                  {step.number}
                </div>
                <div className="ml-3">
                  <div className="text-sm font-medium">{step.title}</div>
                  <div className="text-xs text-muted-foreground">{step.description}</div>
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-0.5 mx-4 ${
                    currentStep > step.number ? 'bg-primary' : 'bg-gray-500'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      <Card className="glass">
        <CardContent className="p-8">
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button 
          variant="outline" 
          onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
          disabled={currentStep === 1}
        >
          Previous
        </Button>
        
        {currentStep < 3 ? (
          <Button 
            variant="default" 
            onClick={() => setCurrentStep(Math.min(3, currentStep + 1))}
          >
            Next
          </Button>
        ) : (
          <Button 
            variant="hero" 
            onClick={handleSubmit}
            className="glow-hover"
          >
            Create Campaign
          </Button>
        )}
      </div>
    </div>
  );
}