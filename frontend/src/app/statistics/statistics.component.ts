import { Component } from '@angular/core';
import { FeatureService } from '../feature-selection/feature.service';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.css']
})
export class StatisticsComponent {
  constructor(private featureService: FeatureService) {}

  downloadStatistics() {
    this.featureService.getFeatureStatistics()
      .subscribe({
        next: data => {
          const blob = new Blob([data], { type: 'text/csv' });
          const link = document.createElement('a');
          
          link.href = window.URL.createObjectURL(blob);
          link.download = 'feature_statistics.csv';
          link.click();
        }, 

        error: (error) => {
          console.error('Error downloading feature statistics:', error);
        }
      });
  }
}
