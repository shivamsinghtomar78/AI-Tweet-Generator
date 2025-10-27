import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';

export const LoadingSkeleton = () => {
  return (
    <Card className="animate-scale-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="h-6 w-6 rounded-full bg-primary/20 animate-pulse"></div>
          <div className="h-6 bg-muted rounded w-1/3 animate-pulse"></div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="h-4 bg-muted rounded w-1/4 animate-pulse"></div>
          <div className="bg-gradient-to-r from-muted to-muted/50 p-4 rounded-lg space-y-3 border border-primary/10">
            <div className="h-4 bg-background/50 rounded animate-pulse"></div>
            <div className="h-4 bg-background/50 rounded w-5/6 animate-pulse" style={{animationDelay: '0.1s'}}></div>
            <div className="h-4 bg-background/50 rounded w-4/6 animate-pulse" style={{animationDelay: '0.2s'}}></div>
          </div>
          <div className="flex gap-2">
            <div className="h-10 bg-muted rounded w-32 animate-pulse"></div>
            <div className="h-10 bg-muted rounded flex-1 animate-pulse" style={{animationDelay: '0.1s'}}></div>
          </div>
        </div>
        <div className="mt-4 text-center">
          <p className="text-sm text-muted-foreground animate-pulse">
            🤖 AI is crafting your perfect tweet...
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
