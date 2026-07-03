import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { uploadImages, compareImages } from '../api/client';
import { UploadCloud, FileImage, Loader2 } from 'lucide-react';
import { cn } from '../utils/cn';

export default function Home() {
  const navigate = useNavigate();
  const [imageA, setImageA] = useState<File | null>(null);
  const [imageB, setImageB] = useState<File | null>(null);

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!imageA || !imageB) throw new Error("Please select both images");
      const uploadRes = await uploadImages(imageA, imageB);
      // Wait for the processing to complete
      const resultRes = await compareImages(uploadRes.id);
      return resultRes;
    },
    onSuccess: (data) => {
      navigate(`/results/${data.id}`);
    }
  });

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>, setter: (f: File) => void) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setter(e.dataTransfer.files[0]);
    }
  }, []);

  const FileDropZone = ({ title, file, setFile }: { title: string, file: File | null, setFile: (f: File) => void }) => (
    <div 
      className={cn(
        "relative flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl transition-all",
        file ? "border-blue-500 bg-blue-500/10" : "border-border hover:border-muted-foreground hover:bg-muted/50"
      )}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => handleDrop(e, setFile)}
    >
      <input 
        type="file" 
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        onChange={(e) => e.target.files && setFile(e.target.files[0])}
        accept=".jpg,.jpeg,.png,.pdf"
      />
      {file ? (
        <div className="flex flex-col items-center gap-2 text-center pointer-events-none">
          <div className="p-3 bg-blue-500/20 text-blue-500 rounded-full">
            <FileImage className="w-8 h-8" />
          </div>
          <div>
            <p className="font-semibold text-sm">{file.name}</p>
            <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3 text-center pointer-events-none text-muted-foreground">
          <div className="p-4 bg-muted rounded-full">
            <UploadCloud className="w-8 h-8" />
          </div>
          <div>
            <p className="font-medium">{title}</p>
            <p className="text-xs mt-1">Drag & drop or click to browse</p>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto flex flex-col items-center">
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">
          AI-Powered Change Detection
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Upload two versions of an image or document. Our Vision Transformer model will detect, localize, and summarize structural differences instantly.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 w-full mb-8">
        <FileDropZone title="Upload Original (Version A)" file={imageA} setFile={setImageA} />
        <FileDropZone title="Upload Modified (Version B)" file={imageB} setFile={setImageB} />
      </div>

      <button
        disabled={!imageA || !imageB || uploadMutation.isPending}
        onClick={() => uploadMutation.mutate()}
        className={cn(
          "flex items-center gap-2 px-8 py-4 rounded-full font-bold text-lg text-white transition-all transform hover:scale-105 shadow-lg shadow-blue-500/20",
          !imageA || !imageB || uploadMutation.isPending 
            ? "bg-muted text-muted-foreground cursor-not-allowed scale-100 shadow-none" 
            : "bg-blue-600 hover:bg-blue-500"
        )}
      >
        {uploadMutation.isPending ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analyzing with AI...
          </>
        ) : (
          "Run Detection Analysis"
        )}
      </button>

      {uploadMutation.isError && (
        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-sm">
          Failed to process images. Please make sure the backend is running.
        </div>
      )}
    </div>
  );
}
