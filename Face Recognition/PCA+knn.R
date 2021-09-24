library(ggplot2)
library(OpenImageR)
library(bmp)
library(e1071)
library(pracma)

#We turn all the pictures into data we can work with
{
names = list.files(pattern = "jpg")
data = matrix(0, length(names),108000)
for (i in 1:length(names)){
  Im = readImage(names[i])
  red = as.vector(Im[,,1])
  green = as.vector(Im[,,2])
  blue = as.vector(Im[,,3])
  data[i,] = t(c(red, green, blue))
}
}
#PCA function
{
PCA=function(data){
  mean=colMeans(data)
  data.scaled=scale(data,center=T,scale=T)
  Sigma_ = data.scaled%*%t(data)/(nrow(data.scaled)-1)
  Eigen = eigen(Sigma_)
  PCs = Eigen$vectors
  Eigenvalues = Eigen$values
  Prop.Var = Eigenvalues/sum(Eigenvalues)
  Cum.Var = cumsum(Eigenvalues)/sum(Eigenvalues)
  PCA=list(mean,PCs,Prop.Var,Cum.Var)
}

PCA=PCA(data)
mean=PCA[[1]]
P=PCA[[2]]
D=PCA[[3]]
Cum.Var=PCA[[4]]

Eigen_=function(data,var){
  data.scaled=scale(data,center=T,scale=T)
  Sigma_ = data.scaled%*%t(data)/(nrow(data.scaled)-1)
  Eigen = eigen(Sigma_)
  Eigenvalues = Eigen$values
  Cummulative.Var = cumsum(Eigenvalues)/sum(Eigenvalues)
  VarLim=min(which(Cummulative.Var>var))
  Eigenvectors = Eigen$vectors[,1:VarLim]
  Eigenfaces = t(data.scaled)%*%Eigenvectors
  return(Eigenfaces)
}




VarLim=min(which(Cum.Var>0.9))
}

###WITH PCA###
{
#INITIAL KNN FUNTION
{
a=NULL
for (i in 1:25){
  a=c(a,rep(i,6))
}

my_knn_ = function(train,test,Eigenfaces,method,k){
  train = t(t(Eigenfaces)%*%t(train))
  test = t(t(Eigenfaces)%*%test)
  temp=NULL
  minimum = NULL
  for (i in 1:nrow(train)){
    x = rbind(test,train[i,])
    temp = c(temp, as.numeric(dist(x, method = method)))
  }
  b=a[sort(temp, index.return = TRUE)$ix[1:k]]
  temp1 <- table(as.vector(b))
  return(as.numeric(names(temp1)[temp1 == max(temp1)]))}
}





Eigenfaces = Eigen_(data,0.9)

tic()
num=sample(1:150,1)
train = data[-num,]
test = data[num,]
my_knn_(train,test,Eigenfaces,"canberra",3)
a[num]
toc()



###Calculating best variances and methods
{
k=3
var=0.9
methods=c("euclidean", "maximum", "manhattan", "canberra")
chek.matrix=matrix(0,4,1)
rownames(chek.matrix)=methods
Eigenfaces = Eigenfaces(data,0.9)

n.rep=20
preds=rep(0,n.rep)
real=rep(0,n.rep)


for (i in 1:4){
  for (n in 1:n.rep){
    num=sample(1:150,1)
    train = data[-num,]
    test = data[num,]
    temp=my_knn_(train,test,Eigenfaces,methods[i],k)
    preds[n]=temp
    real[n]=a[num]
  }
  accuracy=length(which((preds==real)=="TRUE"))/n.rep
  chek.matrix[i,]=accuracy
}


chek.matrix
View(chek.matrix)
}
###Calculating best number of neighbors of the k-nn
{

ks=c(1,3,5,7)
chek.ks=matrix(0,4,2)
chek.ks[,1]=ks
colnames(chek.ks)=c("k","acc")

n.rep=10
preds=rep(0,n.rep)
real=rep(0,n.rep)

for (i in 1:4){
  for (l in 1:n.rep){
    num=sample(1:150,1)
    train = data[-num,]
    test = data[num,]
    temp = my_knn_(train,test,Eigenfaces,"canberra",ks[i])
    preds[l]=temp
    real[l]=a[num]
    }
  accuracy=length(which((preds==real)=="TRUE"))/n.rep
  chek.ks[i,2]=accuracy
}
chek.ks
View(chek.ks)
}
####Calculating the threshold 
{
#Compute all the distances
{

Eigenfaces=Eigen_(data,0.9)
data.scaled=scale(data,center=T,scale=T)
data = data.scaled%*%Eigenfaces


my_knn_all= function(train){
  distance_matrix = matrix(0, nrow(train), nrow(train))
  for (i in 1:nrow(train)){
    temp = NULL
    for (j in 1:nrow(train)){
      x = rbind(train[i,],train[j,])
      temp = as.numeric(dist(x, method = "canberra"))
      distance_matrix[i,j] = temp
    }
  }
  return (as.vector(distance_matrix[distance_matrix>0]))}
#With this function we calculate all the distances and keep them in a vector

values = my_knn_all(data)

df_values1 = as.data.frame(values)
ggplot(data= df_values1, aes(x = values))+
  geom_histogram(bins = 60)+xlab("Values")+ylab("")+labs(title = "All distances")



V1=NULL
for (i in 1:150){
  V1=c(V1,rep(i,149))
}


V2=NULL
for (i in 1:150){
  x=seq(1,150)
  V2=c(V2,which(x!=i))
}


kloko = as.data.frame(cbind(values,V1,V2))
View(kloko)

}
#Compute the threshold
{
max(values)
min(values)
mean(values)
threshold = seq(1, 35, 0.1)

matrix.pred = matrix(0, length(threshold), 3)
colnames(matrix.pred) = c("Threshold", "Real", "Impostor")

matrix.pred[,1] = threshold

for (i in values){
  for (j in 1:length(threshold)){
    if (i < threshold[j]){
      matrix.pred[j,2] = (matrix.pred[j,2] + 1)
    }
    else{
      matrix.pred[j,3] = (matrix.pred[j,3] + 1)
    }
  } 
}

View(matrix.pred)

data1 = as.data.frame(matrix.pred)

ggplot(data1)+aes(x = data1$Threshold, y = data1$Real) +
  geom_line(color = "green")+
  geom_line(aes(x = data1$Threshold, y = data1$Impostor), color = "red")+
  xlab("Threshold") + ylab(NULL) 


reales = data[1:125,]
impostores = data[126:150,]
real.impostors = rep.int(c(0,1), times = c(125, 25))
n.reales=125*124
n.impostores=25*24


ftr_=NULL
tfr_=NULL

x = my_knn_all(reales)
y = my_knn_all(impostores)
for (i in threshold){
  pred.real = (x > i)+0
  pred.impostors = (y > i)+0
  tfr = sum(pred.real == 1)/n.reales
  tfr_ = c(tfr_, tfr)
  
  ftr = sum(pred.impostors == 0)/n.impostores
  ftr_ = c(ftr_, ftr)
  
} 

ggplot()+
  geom_line(aes(x = threshold, y = tfr_),color = "red")+
  geom_line(aes(x = threshold, y = ftr_),color = "green")+
  ylab("")


x=tfr_>ftr_
intercept=threshold[which(diff(x)!=0)]

}
}

###FINAL KNN###
{
a=NULL
for (i in 1:25){
  a=c(a,rep(i,6))
}
  
Eigenfaces=Eigen_(data,0.9)

final_knn_ = function(train, test,Eigenfaces,method,k,threshold){
  
  train = t(t(Eigenfaces)%*%t(train))
  test = t(t(Eigenfaces)%*%test)
  temp=NULL
  for (i in 1:nrow(train)){
    x = rbind(test,train[i,])
    d = as.numeric(dist(x, method = method))
    if (d>threshold){
      d=Inf
    }
    temp = c(temp, d)
  }
  b=a[sort(temp, index.return = TRUE)$ix[1:k]]
  c=sort(temp)[1:5]
  temp1 <- table(as.vector(b))
  temp2 <- table(as.vector(c))
  if (as.numeric(names(temp2)[temp2 == max(temp2)])==Inf){
    return(0)
  }
  return(as.numeric(names(temp1)[temp1 == max(temp1)]))}

n.rep=5
preds=rep(0,n.rep)
real=rep(0,n.rep)


for (l in 1:n.rep){
    num=sample(1:150,1)
    train = data[-num,]
    test = data[num,]
    temp = final_knn_(train,test,Eigenfaces,"canberra",5,17.3)
    preds[l]=temp
    real[l]=a[num]
  }

preds
real
accuracy=length(which((preds==real)=="TRUE"))/n.rep
}

}

###WITHOUT PCA###
{
#INITIAL KNN FUNTION
{
  a=NULL
  for (i in 1:25){
    a=c(a,rep(i,6))
  }
  
  my_knn2 = function(train, test,var,method,k){
    temp=NULL
    minimum = NULL
    for (i in 1:nrow(train)){
      x = rbind(test,train[i,])
      temp = c(temp, as.numeric(dist(x, method = method)))
    }
    b=a[sort(temp, index.return = TRUE)$ix[1:5]]
    temp1 <- table(as.vector(b))
    return(as.numeric(names(temp1)[temp1 == max(temp1)]))}
}


###Calculating best variances and methods
{
  variances=c(0.8, 0.85, 0.9,0.95)
  methods=c("euclidean", "maximum", "manhattan", "canberra")
  chek.matrix=matrix(0,4,4)
  colnames(chek.matrix)=methods
  rownames(chek.matrix)=variances
  
  k=5
  n.rep=10
  preds=rep(0,n.rep)
  real=rep(0,n.rep)
  
  
  for (i in 1:4){
    for (j in 1:4){
      for (l in 1:n.rep){
        num=sample(1:150,1)
        train = data[-num,]
        test = data[num,]
        temp = my_knn2(train,test,variances[i],methods[j],k)
        preds[l]=temp
        real[l]=a[num]
      }
      accuracy=length(which((preds==real)=="TRUE"))/n.rep
      chek.matrix[i,j]=accuracy
    }
  }
  
  chek.matrix
  View(chek.matrix)
}
###Calculating best number of neighbors of the k-nn
{
  
  ks=c(1,3,5,7)
  chek.ks=matrix(0,4,2)
  chek.ks[,1]=ks
  colnames(chek.ks)=c("k","acc")
  
  n.rep=10
  preds=rep(0,n.rep)
  real=rep(0,n.rep)
  
  for (i in 1:4){
    for (l in 1:n.rep){
      num=sample(1:150,1)
      train = data[-num,]
      test = data[num,]
      temp = my_knn2(train,test,0.95,"canberra",k[i])
      preds[l]=temp
      real[l]=a[num]
    }
    accuracy=length(which((preds==real)=="TRUE"))/n.rep
    chek.ks[i,2]=accuracy
  }
  chek.ks
  View(chek.ks)
}
####Calculating the threshold 
{
  #Compute all the distances
  {
    
    my_knn_all2 = function(train){
      distance_matrix = matrix(0, nrow(train), nrow(train))
      for (i in 1:nrow(train)){
        temp = NULL
        for (j in 1:nrow(train)){
          x = rbind(train[i,],train[j,])
          temp = as.numeric(dist(x, method = "canberra"))
          distance_matrix[i,j] = temp
        }
      }
      return (as.vector(distance_matrix[distance_matrix>0]))}
    #With this function we calculate all the distances and keep them in a vector
    
    values = my_knn_all2(data)
    
    df_values1 = as.data.frame(values)
    ggplot(data= df_values1, aes(x = values))+
      geom_histogram(bins = 60)+xlab("Values")+ylab("")+labs(title = "All distances")
    
    
    
    V1=NULL
    for (i in 1:150){
      V1=c(V1,rep(i,149))
    }
    
    
    V2=NULL
    for (i in 1:150){
      x=seq(1,150)
      V2=c(V2,which(x!=i))
    }
    
    
    kloko = as.data.frame(cbind(values,V1,V2))
    View(kloko)
    
  }
  #Compute the threshold
  {
    max(values)
    min(values)
    mean(values)
    threshold = seq(1, 35, 0.1)
    
    matrix.pred = matrix(0, length(threshold), 3)
    colnames(matrix.pred) = c("Threshold", "Real", "Impostor")
    
    matrix.pred[,1] = threshold
    
    for (i in values){
      for (j in 1:length(threshold)){
        if (i < threshold[j]){
          matrix.pred[j,2] = (matrix.pred[j,2] + 1)
        }
        else{
          matrix.pred[j,3] = (matrix.pred[j,3] + 1)
        }
      } 
    }
    
    View(matrix.pred)
    
    data1 = as.data.frame(matrix.pred)
    
    ggplot(data1)+aes(x = data1$Threshold, y = data1$Real) +
      geom_line(color = "green")+
      geom_line(aes(x = data1$Threshold, y = data1$Impostor), color = "red")+
      xlab("Threshold") + ylab(NULL) 
    
    
    reales = data[1:100,]
    impostores = data[101:150,]
    real.impostors = rep.int(c(0,1), times = c(420, 60))
    n.reales=100*99
    n.impostores=50*49
    
    
    ftr_=NULL
    tfr_=NULL
    
    x = my_knn2(reales)
    y = my_knn2(impostores)
    for (i in threshold){
      pred.real = (x > i)+0
      pred.impostors = (y > i)+0
      tfr = sum(pred.real == 1)/n.reales
      tfr_ = c(tfr_, tfr)
      
      ftr = sum(pred.impostors == 0)/n.impostores
      ftr_ = c(ftr_, ftr)
      
    } 
    
    ggplot()+
      geom_line(aes(x = threshold, y = tfr_),color = "red")+
      geom_line(aes(x = threshold, y = ftr_),color = "green")+
      ylab("")
    
    
    x=tfr_>ftr_
    intercept=threshold[which(diff(x)!=0)]
    
  }
}

###FINAL KNN###
{
  a=NULL
  for (i in 1:25){
    a=c(a,rep(i,6))
  }
  
  final_knn2 = function(train, test,variance,method,k,threshold){
    temp=NULL
    for (i in 1:nrow(train)){
      x = rbind(test,train[i,])
      d = as.numeric(dist(x, method = method))
      if (d>threshold){
        d=Inf
      }
      temp = c(temp, d)
    }
    b=a[sort(temp, index.return = TRUE)$ix[1:k]]
    c=sort(temp)[1:5]
    temp1 <- table(as.vector(b))
    temp2 <- table(as.vector(c))
    if (as.numeric(names(temp2)[temp2 == max(temp2)])==Inf){
      return(0)
    }
    return(as.numeric(names(temp1)[temp1 == max(temp1)]))}
  
  n.rep=10
  preds=rep(0,n.rep)
  real=rep(0,n.rep)
  
  
  for (l in 1:n.rep){
    num=sample(1:150,1)
    train = data[-num,]
    test = data[num,]
    temp = final_knn2(train,test,0.95,"canberra",7,27.3)
    preds[l]=temp
    real[l]=a[num]
  }
  
  preds
  real
  accuracy=length(which((preds==real)=="TRUE"))/n.rep
}
}













