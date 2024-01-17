import { Component } from '@angular/core';
import { MenuItem, MessageService } from 'primeng/api';
import { FileService } from '../file-upload/file.service';

@Component({
  selector: 'app-steps',
  templateUrl: './steps.component.html',
  styleUrls: ['./steps.component.css'],
  providers: [MessageService]
})
export class StepsComponent {
  items: Array<MenuItem> = [];
  activeIndex = 0;
  nextStepAllowed = false;

  constructor(private messageService: MessageService, private fileService: FileService) {}

  onActiveIndexChange(event: number): void {
    this.activeIndex = event;
  }

  goToPreviousStep(): void {
    this.activeIndex -= 1;

    if(this.activeIndex < 0) {
      this.activeIndex = 0;
    }

    if (this.activeIndex === 0) {
      this.fileService.clearProcessedFiles().subscribe();
    }
  }

  goToNextStep(): void {
    if (this.nextStepAllowed) {
      this.activeIndex += 1;
      this.nextStepAllowed = false
    }
    
    if (this.activeIndex > this.items.length - 1) {
      this.activeIndex = this.items.length - 1
    }
   }

  onFileSelectionChange(uploadCompleted: boolean): void {
    this.nextStepAllowed = uploadCompleted;
  }

  onFeatureSelectionChange(selectionCompleted: boolean): void {
    this.nextStepAllowed = selectionCompleted;
  }

  onAnnotationStatusChange(annotationCompleted: boolean): void {
    this.nextStepAllowed = annotationCompleted;
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
