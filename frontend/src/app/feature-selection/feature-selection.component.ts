import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { FeatureService } from './feature.service';
import { IFeature } from './feature';

@Component({
  selector: 'app-feature-selection',
  templateUrl: './feature-selection.component.html',
  styleUrls: ['./feature-selection.component.css']
})
export class FeatureSelectionComponent implements OnInit {
  checked: boolean = true;
  selectedFeatures: Array<IFeature> = [];
  allFeatures: Array<IFeature> = [];
  selectedDimensions: Array<string> = [];
  allDimensions: Array<string> = [];
  errorMsg: any;

  constructor(private featureService: FeatureService) {

  }

  onToggleSelectAll() {
    if(this.checked === false) {
      this.featureService.getAllFeatures()
        .subscribe({
          next: (data) => {
            this.selectedFeatures = data;
            this.selectedDimensions = [...new Set(data.map((item) => item.dimension))];
            this.featureService.setSelectedFeatures(this.selectedFeatures);
          }
        })
    } else {
      this.selectedFeatures = [];
      this.selectedDimensions = [];
      this.featureService.setSelectedFeatures(this.selectedFeatures);
    }
  }

  onSelectFeature(event: any) {
    this.selectedFeatures.length === 0 ? this.checked  = true : this.checked = false;

    const dimensionsOfSelectedFeatures = [...new Set(event.checked.map((item: { dimension: string; }) => item.dimension))];
    let allDimensionsSelected: Array<string> = [];
    
    if (dimensionsOfSelectedFeatures.length > 0) {
      dimensionsOfSelectedFeatures.forEach((dimension) => {
        const allFeaturesInDimension = this.allFeatures.filter((feature) => feature.dimension === dimension);
        const selectedFeaturesOfDimension = this.selectedFeatures.filter((feature) => feature.dimension === dimension);

        if (selectedFeaturesOfDimension.length === allFeaturesInDimension.length) {
          if (!allDimensionsSelected.includes(dimension as string)) {
            allDimensionsSelected.push(dimension as string);
          }
        } else {
          allDimensionsSelected.filter((item) => item !== dimension);
        }
      })
    } else {
      allDimensionsSelected = [];
    }

    this.selectedDimensions = allDimensionsSelected;
    this.featureService.setSelectedFeatures(this.selectedFeatures);
  }

  onSelectDimension(dimension: string) {
    const dimensionIndex = this.selectedDimensions.indexOf(dimension);
  
    if (dimensionIndex !== -1) {
      const featuresOfDimension = this.allFeatures.filter((feature) => feature.dimension === dimension);
      this.selectedFeatures = [...this.selectedFeatures, ...featuresOfDimension];
      this.selectedDimensions.push(dimension);
    } else {
      this.selectedDimensions.splice(dimensionIndex, 1);
      this.selectedFeatures = this.selectedFeatures.filter((feature) => feature.dimension !== dimension);
    }
  
    this.featureService.setSelectedFeatures(this.selectedFeatures);
  }

  ngOnInit(): void {
    this.featureService.getAllFeatures().subscribe({
      next: data => {
        this.allFeatures = data;
        this.allDimensions = [...new Set(data.map((item) => item.dimension))]
      }
    })
    
    this.featureService.setSelectedFeatures(this.selectedFeatures);
  }
}
