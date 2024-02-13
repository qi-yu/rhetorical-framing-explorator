import { Injectable } from '@angular/core';
import { MenuItem } from 'primeng/api';

@Injectable({
  providedIn: 'root'
})
export class StepsService {

  constructor() { }

  getSteps(routePath: string | undefined): MenuItem[] {
    switch (routePath) {
      case 'rhetorical-framing':
        return [
          { label: "Upload File" },
          { label: "Select Features" },
          { label: "Start Annotation" },
          { label: "Get Results" },
        ];
        
      case 'keyword':
        return [
          { label: "Upload File" },
          { label: "Select Methods" }
        ];

      default:
          return [];
    }
  }
}
