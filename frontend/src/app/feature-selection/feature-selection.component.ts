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
          }
        })
    } else {
      this.selectedFeatures = [];
      this.selectedDimensions = [];
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
  }

  onSelectDimension(event: any) {
    this.selectedFeatures = this.allFeatures.filter((feature) => event.checked.includes(feature.dimension));
    this.selectedFeatures.length === 0 ? this.checked  = true : this.checked = false;
  }

  ngOnInit(): void {
    this.featureService.getAllFeatures().subscribe({
      next: data => {
        this.allFeatures = data;
        this.allDimensions = [...new Set(data.map((item) => item.dimension))]
      }
    })
  }
}
