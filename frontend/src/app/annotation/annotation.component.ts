import { Component } from '@angular/core';
import { IFeature } from '../feature-selection/feature';
import { FeatureService } from '../feature-selection/feature.service';
import { MessageService } from 'primeng/api';
import { interval, Subscription } from 'rxjs';


@Component({
  selector: 'app-annotation',
  templateUrl: './annotation.component.html',
  styleUrls: ['./annotation.component.css']
})
export class AnnotationComponent {

  selectedFeatures: IFeature[] = [];
  progressValues: { [key: string]: number } = {}; 
  progressSubscription: Subscription | undefined;

  constructor(private featureService: FeatureService, private messageService: MessageService, ) {}

  onStartAnnotation() {
    this.featureService.executeAnnotation(this.selectedFeatures).subscribe({
      next: () => {
        console.log('start annotation');
        this.startProgressPolling();
      },
      error: (err) => this.messageService.add({severity: 'error', summary: 'Error', detail: err})
    });
  }

  startProgressPolling() {
    // Poll for progress updates
    this.progressSubscription = interval(1000).subscribe(() => {
      this.featureService.getProgress().subscribe({
        next: (data) => {
          this.progressValues = data; // Update progress values
          this.updateProgressBars();
          console.log('this.progressValues:', this.progressValues)
        },
        error: (err) => this.messageService.add({ severity: 'error', summary: 'Error', detail: err })
      });
    });
  }

  updateProgressBars() {
    this.selectedFeatures.forEach((feature, index) => {
      setTimeout(() => {
        feature.progress = Number(this.progressValues[feature.annotation_script_name.split('.')[0]]);
        console.log(feature, feature.progress);
      }, index * 1000);
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
    });
  }

}
