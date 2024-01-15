import { Component } from '@angular/core';
import { IFeature } from '../feature-selection/feature';
import { FeatureService } from '../feature-selection/feature.service';
import { MessageService } from 'primeng/api';
import { Message } from 'primeng/api';
import { interval, Subscription } from 'rxjs';


@Component({
  selector: 'app-annotation',
  templateUrl: './annotation.component.html',
  styleUrls: ['./annotation.component.css']
})
export class AnnotationComponent {

  selectedFeatures: IFeature[] = [];
  preprocessingProgressValue: number = 0;
  progressValues: { [key: string]: number } = {}; 
  progressSubscription: Subscription | undefined;
  annotationFinished: boolean = false;
  successMessage: Message[] = [{ 
    severity: 'success', 
    summary: 'Success', 
    detail: 'Annotation finished! Click on "Next Step" to get results.' 
  }]

  constructor(private featureService: FeatureService, private messageService: MessageService, ) {}

  onStartAnnotation() {
    this.featureService.executeAnnotation(this.selectedFeatures).subscribe({
      next: () => {
        this.startProgressPolling();
      },
      error: (err) => this.messageService.add({severity: 'error', summary: 'Error', detail: err})
    });

    this.startProgressPolling();
  }

  startProgressPolling() {
    // Poll for progress updates
    this.progressSubscription = interval(500).subscribe(() => {
      this.featureService.getProgress().subscribe({
        next: (data) => {
          this.progressValues = data; // Update progress values
          this.updateProgressBars();

          setTimeout(() => {
            if(Object.keys(data).length === (this.selectedFeatures.length) + 1  // + 1: progress of preprocessing 
              && Object.values(data).every(value => value === 100)) {
              this.annotationFinished = true;
            }
          }, 1000);
        },
        error: (err) => this.messageService.add({ severity: 'error', summary: 'Error', detail: err })
      });
    });
  }

  updateProgressBars() {
    this.preprocessingProgressValue = Number(this.progressValues['preprocessing']);

    this.selectedFeatures.forEach((feature, index) => {
      feature.progress = Number(this.progressValues[feature.annotation_method]);
    });
  }

  ngOnDestroy() {
    // Unsubscribe from the progress polling when the component is destroyed
    if (this.progressSubscription) {
      this.progressSubscription.unsubscribe();
    }
  }

  ngOnInit() {
    this.featureService.selectedFeatures$.subscribe((features) => {
      this.selectedFeatures = features;
      this.featureService.clearProgress().subscribe();
      this.updateProgressBars();
    });
  }

}
