import { Component } from '@angular/core';
import { IFeature } from '../feature-selection/feature';
import { FeatureService } from '../feature-selection/feature.service';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-annotation',
  templateUrl: './annotation.component.html',
  styleUrls: ['./annotation.component.css']
})
export class AnnotationComponent {

  selectedFeatures: IFeature[] = [];

  constructor(private featureService: FeatureService, private messageService: MessageService, ) {}

  onStartAnnotation() {
    this.featureService.executeAnnotation(this.selectedFeatures).subscribe({
      next: () => {console.log('start annotation');},
      error: (err) => this.messageService.add({severity: 'error', summary: 'Error', detail: err})
    });
  }

  ngOnInit() {
    this.featureService.selectedFeatures$.subscribe((features) => {
      this.selectedFeatures = features;
    });
  }

}
