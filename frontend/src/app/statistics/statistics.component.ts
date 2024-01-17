import { parse } from 'papaparse';
import { Component } from '@angular/core';
import { FeatureService } from '../feature-selection/feature.service';
import { forkJoin } from 'rxjs';
import { IFeature } from '../feature-selection/feature';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.css']
})
export class StatisticsComponent {
  selectedFeatures: Array<IFeature> = [];
  data: any;
  options: any;
  datasetsByGroup: Array<any> = [];

  constructor(private featureService: FeatureService) {}

  downloadStatistics(): void {
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


  configPlot(labels: Array<string>, datasets: Array<any>): void {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    this.data = {
      labels: labels,
      datasets: datasets
    }

    this.options = {
      maintainAspectRatio: false,
      aspectRatio: 0.8,
      plugins: {
          legend: {
              labels: {
                  color: textColor
              }
          }
      },
      scales: {
          x: {
              ticks: {
                  color: textColorSecondary,
                  font: {
                      weight: 500
                  }
              },
              grid: {
                  color: surfaceBorder,
                  drawBorder: false
              }
          },
          y: {
              ticks: {
                  color: textColorSecondary
              },
              grid: {
                  color: surfaceBorder,
                  drawBorder: false
              }
          }

      }
    };
  }


  makePlot(): void {
    this.featureService.selectedFeatures$
      .subscribe((features) => {
        this.selectedFeatures = features;
      });

    this.featureService.getStatisticsByLabel().subscribe({
      next: (raw) => {
        const df: Array<any> = parse(raw, { delimiter: "\t", header: true }).data.slice(0, -1)

        df.forEach((obj) => {
          let currentFeatureData: Array<number> = [];

          this.selectedFeatures.forEach((feature) => {
            currentFeatureData.push(obj[feature.annotation_method])
          })

          this.datasetsByGroup.push({
              label: obj["label"],
              data: currentFeatureData
          })
        })

        this.configPlot(this.selectedFeatures.map(feature => feature.name), this.datasetsByGroup)
      }
    })
  }

  ngOnInit() {
    this.makePlot();    
  }  
}
