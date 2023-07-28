import { Component } from '@angular/core';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-steps',
  templateUrl: './steps.component.html',
  styleUrls: ['./steps.component.css']
})
export class StepsComponent {
  items: Array<MenuItem> = [];
  activeIndex = 0;
  nextStepAllowed = false;

  constructor() {}

  onActiveIndexChange(event: number) {
    this.activeIndex = event;
  }

  goToPreviousStep() {
    this.activeIndex -= 1;

    if(this.activeIndex <= 0) {
      this.activeIndex = 0;
    }
  }

  goToNextStep() {
    if (this.nextStepAllowed) {
      this.activeIndex += 1;
    }
    
    if(this.activeIndex >= this.items.length - 1) {
      this.activeIndex = this.items.length - 1
    }
   }

  onUploadStatusChange(uploadCompleted: boolean) {
    this.nextStepAllowed = uploadCompleted;
  }
  
  ngOnInit() {
    this.items = [
      { label: "Upload File" },
      { label: "Select Features" },
      { label: "Start Annotation" },
      { label: "Get Results" },
    ];
  }
}
