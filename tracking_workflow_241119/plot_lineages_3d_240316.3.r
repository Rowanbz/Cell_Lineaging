#### This is an R script to read the track data 'out.csv', the output of track_cells_240314.5.py, and stick tracks into lineages according to the cell states and locations. 


py_col <- c('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
 '#7f7f7f', '#bcbd22', '#17becf')

d <- read.csv("//Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/3_tracks/out2.csv")
d$edge = as.logical(d$edge=="True")
track_at_edge <- tapply(d$edge, d$track_id, any) # an array of logicals (TRUE/FALSE) with the length of the number of tracks, representing whether each track touches an edge

d$mitotic <- d$mean/d$area*1e3 # array of numeric, high for motitc or dead cells

d$track_id <- factor(d$track_id) # factorize the track_id

tracks <- levels(d$track_id) # list of track_id's




## set the state of each spot
d$state = "I" # interphase, default
d$state[d$mitotic>2] = "M" # mitotic
d$state[d$p_death >0.6] = "D" # dead

d$lineage <- NA # (spot-spot-...-spot) = track, tracks sticked = lineage
d$cell <- NA


######## 1. Plot raw tracks (before stiching) ######

## prepare for 3D plotting
library(rgl) # library for 3D plotting
r3dDefaults$windowRect <- c(0, 0, 1200, 1200)
open3d() 
plot3d(0,0,0, type="n", xlim=c(0, 1200), ylim=c(0,1200), zlim=c(0, 150), xlab="X", ylab="Y", zlab="Time (frames)", lit=FALSE)


## plot tracks in 3D (without sticking)
for (i in 1:length(tracks)) { # loop through tracks
	d1 <- d[d$track_id == tracks[i],] # extract the rows for this track
	d1 <- d1[order(d1$fr),] # sort the rows of this table according to the time frame
	#print(d1[1,])
	if (!track_at_edge[i]) { # skip if the track touches the edge
		lines3d(x=d1$X, y=d1$Y, z=d1$fr, col=py_col[i%%length(py_col)+1], lwd=2) # draw the track in 3D
		text3d(x=d1$X[1], y=d1$Y[1], z=d1$fr[1], col=py_col[i%%length(py_col)+1], texts=tracks[i], offset=15)
		d2 <- d1[d1$state=="M",] # extract the row for mitotic spots
		if (nrow(d2)>0) {
			#scatter3d(x=d2$X, y=d2$Y, z=d2$fr, col=py_col[i%%length(py_col)+1],  surface=FALSE)
			spheres3d(x=d2$X, y=d2$Y, z=d2$fr, col=py_col[i%%length(py_col)+1], radius=4, specular = "black") # draw spheres
		}
		d2 <- d1[d1$state=="D",] # extract the rows for dead cells
		if (nrow(d2)>0) {
			#scatter3d(x=d2$X, y=d2$Y, z=d2$fr, col=py_col[i%%length(py_col)+1],  surface=FALSE)
			spheres3d(x=d2$X, y=d2$Y, z=d2$fr, col="black", radius=2, specular = "black") # draw back spheres
		}
	}
}


###### 2. Stick tracks into lineages #####

max_search_radius <- 30
current_lineage <- 0

## 2-1. Initialize the lineage 
for (i in 1:length(tracks)) {
	d1 <- d[d$track_id == tracks[i],]
	d1 <- d1[order(d1$fr),]
	
	if (d1$fr[1]==1) { # focus on time frame 1
		d$lineage[d$track_id == tracks[i]] <- current_lineage
		d$cell[d$track_id == tracks[i]] <- "0" ## set cell division pattern '0'
		current_lineage <- current_lineage + 1
	}
}

## 2-2. For each track, check whether it starts with "M". If yes, try to find its sister by increasing the search range pixel by pixel.

for (i in 1:length(tracks)) {
	## subtable for a track
	d1 <- d[d$track_id == tracks[i],]
	d1 <- d1[order(d1$fr),]
	
	if ((d1$fr[1]!=1)&(d1$state[1]=="M")) { ## check if the track starts with "M"
		x0 <- d1$X[1]
		y0 <- d1$Y[1]
		d3 <- NULL # reset the table of neaerby cells
		r <- 15 # reset the search range to 15 pixels
		found <- FALSE
		fr_about_to_divide <- d1$fr[1]-1 # observe one frame back
		while ((!found) & (r <= max_search_radius)) {
			# list cells within r from (x0, y0)
			d3 <- d[((d$X-x0)^2+(d$Y-y0)^2 < r^2)&(d$fr==fr_about_to_divide),]
			if (nrow(d3)>0) {
				found <- TRUE
			} else {
				r <- r+1 # if not found in this range, increase r by 1
			}
		}
		
		## if a cell is found in the fr-1 frame and within a search range < set max
		if (found) { 
			d$lineage[d$track_id == tracks[i]] <- d3$lineage[1] # update the linage of this track to be the same id of the found sister
			
			## add a new digit to the cell division pattern code '0' and '1' for a sister pair
			d$cell[d$track_id == tracks[i]] <- paste(d3$cell, "1", sep="") # new brach
			d$cell[(d$track_id == d3$track_id)&(d$fr > fr_about_to_divide)] <- paste(d3$cell, "0", sep="") # new section of the main branch
		} else {
			## if a sister was not found, set this track as a new lineage
			d$lineage[d$track_id == tracks[i]] <- current_lineage
			d$cell[d$track_id == tracks[i]] <- "0"
			current_lineage <- current_lineage + 1
		}
	}
	
	if ((d1$fr[1]!=1)&(d1$state[1]!="M")) { ## if this track first appeared in fr>1 as non-mitotic cell, simple treat it as a new lineage
		d$lineage[d$track_id == tracks[i]] <- current_lineage
		d$cell[d$track_id == tracks[i]] <- "0"
		current_lineage <- current_lineage + 1
	}
}


########## 3. Plot the stiched lineages in 3D ########## 
## use the same color for all the tracks that belong to the same lineage.
open3d() 
plot3d(0,0,0, type="n", xlim=c(0, 1200), ylim=c(0,1200), zlim=c(0, 150), xlab="X", ylab="Y", zlab="Time (frames)", lit=FALSE)

for (i in 1:length(tracks)) {
	d1 <- d[d$track_id == tracks[i],]
	d1 <- d1[order(d1$fr),]
	#print(d1[1,])
	if (!track_at_edge[i]) {
		lineage_color <- py_col[d1$lineage[1]%%length(py_col)+1] # color of the lineage to which this track belongs
		lines3d(x=d1$X, y=d1$Y, z=d1$fr, col=lineage_color, lwd=2)
		text3d(x=d1$X[1], y=d1$Y[1], z=d1$fr[1], col=lineage_color, texts=tracks[i], offset=15)
		d2 <- d1[d1$state=="M",]
		if (nrow(d2)>0) {
			#scatter3d(x=d2$X, y=d2$Y, z=d2$fr, col=py_col[i%%length(py_col)+1],  surface=FALSE)
			spheres3d(x=d2$X, y=d2$Y, z=d2$fr, col=lineage_color, radius=4, specular = "black")
		}
		d2 <- d1[d1$state=="D",]
		if (nrow(d2)>0) {
			#scatter3d(x=d2$X, y=d2$Y, z=d2$fr, col=py_col[i%%length(py_col)+1],  surface=FALSE)
			spheres3d(x=d2$X, y=d2$Y, z=d2$fr, col="black", radius=2, specular = "black")
		}
		#print(d1$lineage[1]%%length(py_col)+1)
	}
}



######## 4. Plot 2D lineage schematics #########


#### function to trace the branches of a tree
## each spot has 'cell', the code for cell division pattern
## '0' -> '00' and '01
## '00' -> '000' and '001'
## '01' -> '010' and '011'
## ....
## note this function is recursive (see eg. https://www.programiz.com/python-programming/recursion) 
get_daughters <- function(d_lin, cell_id) {
	if (nchar(cell_id)<4) {
		cell0 <- paste(cell_id, "0", sep="")
		cell1 <- paste(cell_id, "1", sep="")
		d0 <- d_lin[d_lin$cell==cell0,]
		if (nrow(d0)>0) {
			cell0_frames <- c(min(d0$fr), max(d0$fr))
			print(cell0)
			print(cell0_frames)
			get_daughters(d_lin, cell0)
		}
		d1 <- d_lin[d_lin$cell==cell1,]
		if (nrow(d1)>0) {
			cell1_frames <- c(min(d1$fr), max(d1$fr))
			print(cell1)
			print(cell1_frames)
			get_daughters(d_lin, cell1)
		}
	}
}	

## another recursive function to draw a tree
draw_daughters <- function(d_lin, cell_id, x, dx, ...) {
	if (nchar(cell_id)<4) {
		cell0 <- paste(cell_id, "0", sep="")
		cell1 <- paste(cell_id, "1", sep="")

		d0 <- d_lin[d_lin$cell==cell0,]
		d0 <- d0[order(d0$fr),]
		if (nrow(d0)>0) {
			cell0_frames <- c(min(d0$fr), max(d0$fr))
			#print(cell0)
			#print(cell0_frames)
			text(x-dx, cell0_frames[1], d0$track_id[1])
			segments(x, cell0_frames[1]-1, x-dx, cell0_frames[1], ...)
			segments(x-dx, cell0_frames[1], x-dx, cell0_frames[2], ...)
			draw_daughters(d_lin, cell0, x-dx, dx/2, ...)
		}
		d1 <- d_lin[d_lin$cell==cell1,]
		d1 <- d1[order(d1$fr),]
		if (nrow(d1)>0) {
			cell1_frames <- c(min(d1$fr), max(d1$fr))
			#print(cell1)
			#print(cell1_frames)
			text( x+dx, cell1_frames[1], d1$track_id[1])
			segments(x, cell1_frames[1]-1, x+dx, cell1_frames[1], ...)
			segments(x+dx, cell1_frames[1], x+dx, cell1_frames[2], ...)
			draw_daughters(d_lin, cell1, x+dx, dx/2, ...)
		}
	}
}	



df <- d[!is.na(d$lineage),]

n_rows <- 5
n_per_row <- 40
lineages <- levels(factor(df$lineage))
for (i in 1:length(lineages)) {
	if ((i-1)%%(n_per_row*n_rows)==0) {
		quartz(width=15, height=8)
		par(mfrow=c(n_rows,1), mar=c(2, 2, 1, 0), mgp=c(2.1, 0.7, 0),las=1)
	}

	if ((i-1)%%n_per_row==0) {
		plot(0, 0, type="n", xlim=c(n_per_row*(i%/%n_per_row), n_per_row*(i%/%n_per_row+1)), ylim=c(150, 0), bty="n", axes=FALSE, lwd=2)
		axis(2)
	}
	
	d_lin <- df[df$lineage==lineages[i],]
	d0 <- d_lin[d_lin$cell=="0",]
	d0 <- d0[order(d0$fr),]
	col <- py_col[d0$lineage[1]%%length(py_col)+1]
	cell0_frames <- c(min(d0$fr), max(d0$fr))
	x = i
	text(x, cell0_frames[1], d0$track_id[1])
	segments(x, cell0_frames[1], x, cell0_frames[2], col=col, lwd=2)
	draw_daughters(d_lin, "0", x, 0.25, col=col, lwd=2)
}
