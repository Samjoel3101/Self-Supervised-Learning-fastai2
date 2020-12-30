# Self Supervised Learning with fastai2

Implementations of self supervised models with fastai2.I've implemented models like SimClr, CGD, BDB networks in fastai. You can also build your own models with the underlying self supervised learning building blocks in this package. This package also provides loss flexibility where different losses can be applied to different outcomes of the network i.e for semi supervised learning you can apply classification loss(cross entropy loss) for the classification head and unsupervised loss(Triplet, NtXent, Contrastive Loss ..etc) for the representation head. Representation Head is the branch of your network which learns feature representations of the image. This can be used to train our models on large unlabelled datasets which produce good representations of our image which then can be used in tasks like clustering similar images and image retrieval tasks. 
The Image below is taken from https://arxiv.org/pdf/1903.10663.pdf
![](https://github.com/Samjoel3101/Self-Supervised-Learning-fastai2/blob/master/cgd%20image.png)

