import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getResult, getAssetUrl, getReportUrl } from '../api/client';
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';
import { Download, AlertTriangle, Layers, BarChart3, FileText, CheckCircle2, ChevronLeft } from 'lucide-react';
import { cn } from '../utils/cn';

export default function Results() {
  const { id } = useParams<{ id: string }>();
  
  const { data, isLoading, isError } = useQuery({
    queryKey: ['result', id],
    queryFn: () => getResult(id!),
    enabled: !!id,
    refetchInterval: (query) => (query.state.data?.status === 'processing' ? 2000 : false),
  });

  const [activeTab, setActiveTab] = useState<'slider' | 'overlay' | 'heatmap' | 'bbox'>('slider');

  if (isLoading || data?.status === 'processing' || data?.status === 'uploaded') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <h2 className="text-xl font-medium animate-pulse text-muted-foreground">Running Vision Transformer Analysis...</h2>
      </div>
    );
  }

  if (isError || !data || data.status.startsWith('failed')) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 text-red-500">
        <AlertTriangle className="w-16 h-16" />
        <h2 className="text-xl font-medium">Failed to load results.</h2>
        <Link to="/" className="text-blue-500 hover:underline mt-4">Go back to home</Link>
      </div>
    );
  }

  const { statistics, summary } = data;
  
  const renderVisualizer = () => {
    switch (activeTab) {
      case 'slider':
        return (
          <ReactCompareSlider
            itemOne={<ReactCompareSliderImage src={getAssetUrl(data.original_a_url)} alt="Original A" />}
            itemTwo={<ReactCompareSliderImage src={getAssetUrl(data.original_b_url)} alt="Original B" />}
            className="w-full h-full object-contain bg-muted/20 rounded-xl"
          />
        );
      case 'overlay':
        return <img src={getAssetUrl(data.overlay_url)} alt="Overlay" className="w-full h-full object-contain rounded-xl bg-muted/20" />;
      case 'heatmap':
        return <img src={getAssetUrl(data.heatmap_url)} alt="Heatmap" className="w-full h-full object-contain rounded-xl bg-muted/20" />;
      case 'bbox':
        return <img src={getAssetUrl(data.bbox_url)} alt="Bounding Boxes" className="w-full h-full object-contain rounded-xl bg-muted/20" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      <div className="flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ChevronLeft className="w-4 h-4" /> Back to Upload
        </Link>
        <div className="flex items-center gap-3">
          <a 
            href={getReportUrl(data.id)} 
            download
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <Download className="w-4 h-4" /> Export PDF Report
          </a>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        
        {/* Main Visualizer (Left - 2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between bg-card p-2 rounded-lg border border-border">
            <div className="flex items-center gap-2 p-1">
              {(['slider', 'overlay', 'heatmap', 'bbox'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={cn(
                    "px-4 py-2 rounded-md text-sm font-medium transition-all capitalize",
                    activeTab === tab ? "bg-blue-500 text-white shadow-sm" : "text-muted-foreground hover:bg-muted"
                  )}
                >
                  {tab}
                </button>
              ))}
            </div>
            <div className="pr-4 text-sm text-muted-foreground flex items-center gap-2">
              <Layers className="w-4 h-4" /> High-Res View
            </div>
          </div>
          
          <div className="aspect-[4/3] w-full bg-card border border-border rounded-xl overflow-hidden shadow-sm relative">
             {renderVisualizer()}
          </div>
        </div>

        {/* Info Panels (Right - 1 Col) */}
        <div className="space-y-6">
          
          {/* Summary Panel */}
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="flex items-center gap-2 text-lg font-bold mb-4">
              <FileText className="w-5 h-5 text-blue-500" /> 
              AI Analysis Summary
            </h3>
            <div className="p-4 bg-blue-500/10 rounded-lg text-blue-100/90 leading-relaxed text-sm border border-blue-500/20">
              {summary}
            </div>
          </div>

          {/* Stats Panel */}
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="flex items-center gap-2 text-lg font-bold mb-4">
              <BarChart3 className="w-5 h-5 text-indigo-500" /> 
              Detection Statistics
            </h3>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-muted/50 rounded-lg border border-border">
                <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">Changed Areas</p>
                <p className="text-3xl font-extrabold text-foreground">{statistics?.changed_regions}</p>
              </div>
              <div className="p-4 bg-muted/50 rounded-lg border border-border">
                <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">Total Impact</p>
                <p className="text-3xl font-extrabold text-foreground">{statistics?.percentage}%</p>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Region Details</h4>
              {statistics?.regions.length === 0 ? (
                <div className="flex items-center gap-2 text-green-500 text-sm">
                  <CheckCircle2 className="w-4 h-4" /> No changes found
                </div>
              ) : (
                <div className="max-h-60 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                  {statistics?.regions.map((region: any, i: number) => (
                    <div key={i} className="flex flex-col p-3 rounded-lg border border-border bg-muted/30 hover:bg-muted/60 transition-colors">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="text-sm font-bold text-foreground">Change #{region.id}</p>
                          <p className="text-xs text-muted-foreground capitalize mt-1">{region.location} &bull; {region.area} px²</p>
                        </div>
                        <div className="text-right">
                          <span className={cn(
                            "inline-block px-2 py-1 rounded text-xs font-bold uppercase",
                            region.severity === 'High' ? 'bg-red-500/20 text-red-500' :
                            region.severity === 'Medium' ? 'bg-yellow-500/20 text-yellow-500' :
                            'bg-blue-500/20 text-blue-500'
                          )}>
                            {region.severity}
                          </span>
                        </div>
                      </div>
                      
                      {region.crop_a_url && region.crop_b_url && (
                        <div className="flex gap-2 w-full mt-2 bg-card p-2 rounded border border-border/50">
                          <div className="flex-1 flex flex-col items-center">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">Original</span>
                            <img src={getAssetUrl(region.crop_a_url)} alt="Original Crop" className="w-full h-auto rounded object-contain bg-muted" />
                          </div>
                          <div className="flex-1 flex flex-col items-center">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">Modified</span>
                            <img src={getAssetUrl(region.crop_b_url)} alt="Modified Crop" className="w-full h-auto rounded object-contain bg-muted" />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
