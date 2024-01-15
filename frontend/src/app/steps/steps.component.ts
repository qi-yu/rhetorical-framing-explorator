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

  onActiveIndexChange(event: number) {
    this.activeIndex = event;
  }

  goToPreviousStep() {
    this.activeIndex -= 1;

    if(this.activeIndex < 0) {
      this.activeIndex = 0;
    }

    if (this.activeIndex === 0) {
      this.fileService.clearProcessedFiles().subscribe();
    }
  }

  goToNextStep() {
    if (this.nextStepAllowed) {
      this.activeIndex += 1;
    }
    
    if (this.activeIndex > this.items.length - 1) {
      this.activeIndex = this.items.length - 1
    }
   }

  onFileSelectionChange(uploadCompleted: boolean) {
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
