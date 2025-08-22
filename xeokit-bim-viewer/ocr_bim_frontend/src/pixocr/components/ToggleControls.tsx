'use client';

import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';

interface ToggleControlsProps {
  translateHeaders: boolean;
  onTranslateHeadersChange: (value: boolean) => void;
  enableValidation: boolean;
  onEnableValidationChange: (value: boolean) => void;
}

export default function ToggleControls({
  translateHeaders,
  onTranslateHeadersChange,
  enableValidation,
  onEnableValidationChange,
}: ToggleControlsProps) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Processing Options</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Label htmlFor="translate-headers" className="flex-1">
            <div>
              <div className="font-medium">Translate Column Headers</div>
              <div className="text-sm text-gray-500">
                Automatically translate table headers to English
              </div>
            </div>
          </Label>
          <Switch
            id="translate-headers"
            checked={translateHeaders}
            onCheckedChange={onTranslateHeadersChange}
          />
        </div>

        <div className="flex items-center justify-between">
          <Label htmlFor="enable-validation" className="flex-1">
            <div>
              <div className="font-medium">Enable Schema Validation</div>
              <div className="text-sm text-gray-500">
                Validate extracted data against predefined schemas
              </div>
            </div>
          </Label>
          <Switch
            id="enable-validation"
            checked={enableValidation}
            onCheckedChange={onEnableValidationChange}
          />
        </div>
      </div>
    </Card>
  );
}